from celery import shared_task
from django.utils import timezone
from .models import Product, Review, QuestionAnswer
from .scraper import AmazonProductScraper
from .embeddings import EmbeddingService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_and_embed_product(self, product_id):
    """
    Celery task to scrape product data and create embeddings
    """
    try:
        # Get product
        product = Product.objects.get(id=product_id)
        product.status = 'scraping'
        product.save()
        
        logger.info(f"Starting scraping for product {product_id}: {product.url}")
        
        # Scrape data
        scraper = AmazonProductScraper()
        scraped_data = scraper.scrape_product_data(product.url)
        
        if not scraped_data:
            raise Exception("No data scraped")
        
        # Update product with scraped data
        product.title = scraped_data.get('title', '')
        product.brand = scraped_data.get('brand', '')
        product.current_price = scraped_data.get('current_price', '')
        product.original_price = scraped_data.get('original_price', '')
        product.availability = scraped_data.get('availability', '')
        product.features = scraped_data.get('features', '')
        product.specifications = scraped_data.get('specifications', {})
        product.categories = scraped_data.get('categories', [])
        product.variants = scraped_data.get('variants', [])
        product.sales_rank = scraped_data.get('sales_rank', '')
        product.related_products = scraped_data.get('related_products', [])
        product.shipping_info = scraped_data.get('shipping_info', [])
        product.scraped_at = timezone.now()
        product.status = 'embedding'
        product.save()
        
        logger.info(f"Scraped product data for {product_id}")
        
        # Save reviews
        reviews = scraped_data.get('reviews', [])
        for review_data in reviews:
            Review.objects.create(
                product=product,
                title=review_data.get('title', ''),
                text=review_data.get('text', ''),
                rating=review_data.get('rating', ''),
                customer_name=review_data.get('customer_name', ''),
                helpful_votes=review_data.get('helpful_votes', '')
            )
        
        logger.info(f"Saved {len(reviews)} reviews for product {product_id}")
        
        # Save Q&A
        qa_list = scraped_data.get('qa', [])
        for qa_text in qa_list:
            QuestionAnswer.objects.create(
                product=product,
                question=qa_text,
                answer=''
            )
        
        logger.info(f"Saved {len(qa_list)} Q&A for product {product_id}")
        
        # Create embeddings
        embedding_service = EmbeddingService()
        scraped_text = scraped_data.get('scraped_text', '')
        
        if not scraped_text:
            raise Exception("No text to embed")
        
        vector_count = embedding_service.create_embeddings(
            product_id=str(product.id),
            text=scraped_text
        )
        
        # Update product
        product.pinecone_namespace = embedding_service.create_namespace(str(product.id))
        product.vector_count = vector_count
        product.status = 'completed'
        product.error_message = None
        product.save()
        
        logger.info(
            f"Successfully completed scraping and embedding for product {product_id}"
        )
        
        return {
            'product_id': str(product_id),
            'status': 'completed',
            'vector_count': vector_count
        }
        
    except Exception as e:
        logger.error(
            f"Error in scrape_and_embed_product for {product_id}: {str(e)}",
            exc_info=True
        )
        
        # Update product status
        try:
            product = Product.objects.get(id=product_id)
            product.status = 'failed'
            product.error_message = str(e)
            product.save()
        except:
            pass
        
        # Retry task
        raise self.retry(exc=e)


@shared_task
def cleanup_old_products(days=30):
    """
    Celery task to cleanup old products
    """
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    old_products = Product.objects.filter(created_at__lt=cutoff_date)
    
    # Delete embeddings from Pinecone
    embedding_service = EmbeddingService()
    for product in old_products:
        try:
            embedding_service.delete_product_embeddings(str(product.id))
        except Exception as e:
            logger.error(f"Error deleting embeddings for {product.id}: {str(e)}")
    
    # Delete from database
    count = old_products.count()
    old_products.delete()
    
    logger.info(f"Cleaned up {count} old products")
    return {'deleted_count': count}
