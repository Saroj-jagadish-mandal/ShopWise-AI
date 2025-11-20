from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from django.conf import settings
import logging
import hashlib

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for creating and managing embeddings in Pinecone"""
    
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )
    
    def create_namespace(self, product_id):
        """Create unique namespace for product"""
        return f"product_{product_id}"
    
    def split_text(self, text):
        """Split text into chunks"""
        if not text:
            return []
        return self.text_splitter.split_text(text)
    
    def create_embeddings(self, product_id, text, batch_size=50):
        """
        Create embeddings and store in Pinecone
        Returns: number of vectors stored
        """
        try:
            # Split text
            chunks = self.split_text(text)
            if not chunks:
                logger.warning(f"No chunks created for product {product_id}")
                return 0
            
            logger.info(f"Created {len(chunks)} chunks for product {product_id}")
            
            # Create namespace
            namespace = self.create_namespace(product_id)
            
            # Process in batches
            vectors_stored = 0
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                
                # Generate embeddings
                embeddings = self.embeddings.embed_documents(batch)
                
                # Prepare vectors for Pinecone
                vectors = []
                for j, (chunk, embedding) in enumerate(zip(batch, embeddings)):
                    vector_id = f"{product_id}_chunk_{i+j}"
                    vectors.append({
                        'id': vector_id,
                        'values': embedding,
                        'metadata': {
                            'product_id': str(product_id),
                            'chunk_index': i + j,
                            'text': chunk[:1000]  # Store first 1000 chars
                        }
                    })
                
                # Upsert to Pinecone
                self.index.upsert(vectors=vectors, namespace=namespace)
                vectors_stored += len(vectors)
                
                logger.info(
                    f"Upserted batch {i//batch_size + 1} "
                    f"({len(vectors)} vectors) to Pinecone"
                )
            
            logger.info(
                f"Successfully stored {vectors_stored} vectors "
                f"for product {product_id} in namespace {namespace}"
            )
            return vectors_stored
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}", exc_info=True)
            raise
    
    def query_similar(self, product_id, query_text, top_k=2):
        """
        Query similar chunks for a product
        Returns: list of matching chunks with scores
        """
        try:
            # Create query embedding
            query_embedding = self.embeddings.embed_query(query_text)
            
            # Query Pinecone
            namespace = self.create_namespace(product_id)
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                include_metadata=True
            )
            
            # Extract results
            matches = []
            for match in results.matches:
                matches.append({
                    'id': match.id,
                    'score': match.score,
                    'text': match.metadata.get('text', ''),
                    'chunk_index': match.metadata.get('chunk_index', 0)
                })
            
            logger.info(f"Found {len(matches)} matches for query: {query_text[:50]}")
            return matches
            
        except Exception as e:
            logger.error(f"Error querying embeddings: {str(e)}", exc_info=True)
            raise
    
    def delete_product_embeddings(self, product_id):
        """Delete all embeddings for a product"""
        try:
            namespace = self.create_namespace(product_id)
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Deleted all vectors for product {product_id}")
        except Exception as e:
            logger.error(f"Error deleting embeddings: {str(e)}", exc_info=True)
            raise