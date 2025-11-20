# products/scraper.py (PLAYWRIGHT MIGRATION)

import json
import time
from playwright.sync_api import sync_playwright, TimeoutError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# --- Synchronous Playwright Implementation ---

class AmazonProductScraper:
    """Amazon product scraper migrated to Playwright for reliable driver management."""
    
    def __init__(self):
        # Playwright manages the driver path internally, so we don't need a path here.
        self.headless = True # Set to True for production background scraping
        self.browser = None
        self.page = None

    def setup_browser(self, p):
        """Setup Playwright browser instance."""
        logger.info("Launching Playwright browser (Chromium)...")
        # Playwright automatically handles the browser executable version
        self.browser = p.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox'] 
        )
        self.page = self.browser.new_page()
        
        # Set User-Agent and anti-bot headers
        self.page.set_extra_http_headers({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        })

    def safe_find_element(self, selector, timeout=3):
        """Find element using Playwright locator with error handling."""
        try:
            # Playwright's locator().is_visible() is the safest way to check existence and visibility.
            locator = self.page.locator(selector).first
            locator.wait_for(state="attached", timeout=timeout * 1000)
            return locator
        except TimeoutError:
            return None
            
    def extract_text_safe(self, locator):
        """Extract text from Playwright locator."""
        try:
            return locator.inner_text().strip()
        except Exception:
            return ""

    def extract_attribute_safe(self, locator, attribute):
        """Extract attribute from Playwright locator."""
        try:
            return locator.get_attribute(attribute)
        except Exception:
            return ""

    def scrape_product_data(self, product_url):
        """Main scraping method using synchronous Playwright execution."""
        
        # Use sync_playwright as the execution context for the synchronous Celery task
        with sync_playwright() as p:
            try:
                self.setup_browser(p)
                logger.info(f"Navigating to: {product_url}")
                self.page.goto(product_url, timeout=60000) # 60 sec timeout
                
                # Wait for critical element (product title)
                self.page.wait_for_selector("#productTitle", timeout=8000)
                logger.info("Page loaded...")
                
                product_data = {}
                
                # --- 1. Product Title (FIXED: Use :visible to avoid strict mode error) ---
                title_locator = self.page.locator("#productTitle:visible")
                product_data['title'] = self.extract_text_safe(title_locator)
                
                # --- 2. Price Information ---
                price_locator = self.page.locator(".a-price .a-offscreen").first
                product_data['current_price'] = self.extract_text_safe(price_locator)
                price_orig_locator = self.page.locator(".a-text-price .a-offscreen").first
                product_data['original_price'] = self.extract_text_safe(price_orig_locator)
                
                # --- 3. Product Features ---
                features_locator = self.page.locator("#feature-bullets")
                product_data['features'] = self.extract_text_safe(features_locator)
                
                # --- 4. Product Specifications ---
                product_data['specifications'] = self._extract_specifications_pw()
                
                # --- 6. Brand Information ---
                product_data['brand'] = self.extract_text_safe(self.page.locator("#bylineInfo"))
                
                # --- 7. Availability Status ---
                product_data['availability'] = self.extract_text_safe(self.page.locator("#availability"))
                
                # --- 8. Product Variants ---
                variants_locators = self.page.locator("#variation_size_name li, #variation_color_name li").all()
                product_data['variants'] = [self.extract_text_safe(v) for v in variants_locators if self.extract_text_safe(v)]
                
                # --- 9. Customer Questions & Answers ---
                qa_locators = self.page.locator("#ask-btf_feature_div .a-section").all()
                product_data['qa'] = [self.extract_text_safe(qa) for qa in qa_locators[:10] if self.extract_text_safe(qa)]
                
                # --- 10. Related Products (Simplified) ---
                product_data['related_products'] = self._extract_related_products_pw()
                
                # --- 11. Categories ---
                categories_locators = self.page.locator("#wayfinding-breadcrumbs_feature_div a").all()
                product_data['categories'] = [self.extract_text_safe(c) for c in categories_locators if self.extract_text_safe(c)]
                
                # --- 12. Shipping Information ---
                shipping_locators = self.page.locator("#mir-layout-DELIVERY_BLOCK").all()
                product_data['shipping_info'] = [self.extract_text_safe(s) for s in shipping_locators if self.extract_text_safe(s) and len(self.extract_text_safe(s)) > 5]
                
                # --- 13. Best Seller Rank ---
                product_data['sales_rank'] = self.extract_text_safe(self.page.locator("#SalesRank"))
                
                # --- 5. Customer Reviews (Run last, includes pagination) ---
                product_data['reviews'] = self._extract_reviews_pw()
                
                # --- 14. Concatenate text for RAG (Re-used existing logic) ---
                product_data['scraped_text'] = self._create_scraped_text(product_data)
                
                logger.info("Data extraction completed successfully!")
                return product_data
                
            except Exception as e:
                logger.error(f"Error occurred while scraping: {str(e)}", exc_info=True)
                raise # Raise exception for Celery to mark as failed
            finally:
                if self.browser:
                    self.browser.close()

    # --- Helper Methods for Cleaner Code ---

    def _extract_specifications_pw(self):
        """Extract product specifications."""
        specifications = {}
        spec_selectors = [
            "#productDetails_techSpec_section_1 tr",
            "#productDetails_detailBullets_sections1 tr",
            "#prodDetails tr",
            ".prodDetTable tr"
        ]
        
        for selector in spec_selectors:
            for spec in self.page.locator(selector).all():
                try:
                    key = self.extract_text_safe(spec.locator("td:first-child, th"))
                    value = self.extract_text_safe(spec.locator("td:last-child"))
                    if key and value and key != value:
                        specifications[key] = value
                except Exception:
                    continue
        return specifications

    def _extract_related_products_pw(self):
        """Extract related products."""
        related_products = []
        selectors = [
            "[data-automation-id='related-products'] a",
            "#similarities a"
        ]
        
        for selector in selectors:
            for related in self.page.locator(selector).all()[:10]:
                title = self.extract_attribute_safe(related, 'title')
                href = self.extract_attribute_safe(related, 'href')
                if title and href:
                    if not href.startswith('http'):
                        href = self.page.url.split('/dp/')[0] + href # Base URL logic
                    related_products.append({'title': title, 'url': href})
        return related_products

    def _extract_reviews_pw(self):
        """Extract customer reviews with pagination (up to max_pages)."""
        reviews = []
        review_selector = ".a-section.review, #cm-cr-dp-review-list .review"
        page_count = 1
        max_pages = 5
        
        if self.page.locator("#customerReviews").count() == 0:
            return reviews # No reviews section
            
        # Click 'See all reviews' if present
        see_more = self.safe_find_element("a[data-hook='see-all-reviews-link']")
        if see_more:
            try:
                see_more.click()
                self.page.wait_for_load_state('networkidle', timeout=5000)
                logger.info("Navigated to dedicated review page.")
            except Exception:
                logger.warning("Could not click 'See more reviews'")
        
        while page_count <= max_pages:
            logger.info(f"Scraping reviews from page {page_count}...")
            
            # Use page.wait_for_selector to handle AJAX loading
            try:
                self.page.wait_for_selector(review_selector, timeout=5000)
            except TimeoutError:
                break # Timeout means no reviews loaded
                
            review_elements = self.page.locator(review_selector).all()
            
            for review in review_elements:
                try:
                    data = {}
                    data['title'] = self.extract_text_safe(review.locator(".review-title"))
                    # Note: Using text content for the review body
                    data['text'] = self.extract_text_safe(review.locator(".a-expander-content.reviewText.review-text-content.a-expander-partial-collapse-content"))
                    data['rating'] = self.extract_text_safe(review.locator(".review-rating"))
                    data['customer_name'] = self.extract_text_safe(review.locator("span.a-profile-name"))
                    data['helpful_votes'] = self.extract_text_safe(review.locator(".a-size-small.a-color-secondary")) or "0 people found this helpful"
                    
                    if data['text']:
                        reviews.append(data)
                except Exception as e:
                    logger.warning(f"Error processing review on page {page_count}: {str(e)}")
                    continue
            
            # Check for 'Next page' button
            next_page_locator = self.page.locator("li.a-last a")
            if next_page_locator.count() == 0 or not next_page_locator.is_enabled():
                logger.info(f"No more review pages found after page {page_count}")
                break
                
            try:
                next_page_locator.click()
                self.page.wait_for_load_state('networkidle', timeout=5000)
                page_count += 1
            except Exception:
                logger.warning(f"Could not click 'Next page' on page {page_count}")
                break
                
        return reviews

    def _create_scraped_text(self, product_data):
        """Create concatenated text for RAG pipeline (same logic)."""
        text_parts = []
        
        # Title and basic info
        if product_data.get('title'):
            text_parts.append(f"Title: {product_data['title']}")
        if product_data.get('features'):
            text_parts.append(f"Features:\n{product_data['features']}")
        
        # Specifications
        if product_data.get('specifications'):
            text_parts.append("Specifications:")
            for key, value in product_data['specifications'].items():
                text_parts.append(f"  {key}: {value}")
        
        # Reviews
        if product_data.get('reviews'):
            text_parts.append("\nCustomer Reviews:")
            for review in product_data['reviews']:
                review_text = (
                    f"Review by {review.get('customer_name', 'Anonymous')}: "
                    f"{review.get('title', '')} - {review.get('text', '')} "
                    f"(Rating: {review.get('rating', 'N/A')}, Helpful: {review.get('helpful_votes', 'N/A')})"
                )
                text_parts.append(review_text)
        
        # Q&A
        if product_data.get('qa'):
            text_parts.append("\nQuestions & Answers:")
            for qa in product_data['qa']:
                text_parts.append(f"  {qa}")
        
        return "\n".join(text_parts)