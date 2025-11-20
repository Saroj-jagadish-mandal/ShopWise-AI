from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from django.core.cache import cache
from django.conf import settings
from .embeddings import EmbeddingService
import logging

logger = logging.getLogger(__name__)


class QAService:
    """Service for handling Q&A with RAG"""
    
    def __init__(self):
        self.llm = GoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=settings.GOOGLE_API_KEY
        )
        self.embedding_service = EmbeddingService()
        
        self.prompt_template = """
You are an expert assistant answering questions about an Amazon product based on the provided context.

Use the context to provide accurate, concise, and helpful answers. Focus on key product details like title, price, features, or reviews when relevant.

If the exact answer isn't in the context, use the available information to give a reasonable response or clarify what information is missing.

Format your answer clearly, using bullet points or short paragraphs for readability.

Context:
{context}

Chat History:
{chat_history}

Question: {question}

Answer:"""
        
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "chat_history", "question"]
        )
    
    def get_answer(self, product_id, question, chat_history=None):
        """
        Get answer for a question using RAG
        
        Args:
            product_id: UUID of the product
            question: User's question
            chat_history: List of previous messages
            
        Returns:
            dict with answer and context chunks
        """
        try:
            # Check cache
            cache_key = f"qa_{product_id}_{hash(question)}"
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for question: {question[:50]}")
                return cached_result
            
            # Get similar chunks
            matches = self.embedding_service.query_similar(
                product_id=str(product_id),
                query_text=question,
                top_k=5
            )
            
            if not matches:
                return {
                    'answer': "I don't have enough information to answer this question.",
                    'context_chunks': []
                }
            
            # Prepare context
            context = "\n\n".join([match['text'] for match in matches])
            
            # Prepare chat history
            history_text = ""
            if chat_history:
                history_text = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in chat_history[-5:]  # Last 5 messages
                ])
            
            # Generate answer
            formatted_prompt = self.prompt.format(
                context=context,
                chat_history=history_text,
                question=question
            )
            
            answer = self.llm.invoke(formatted_prompt)
            
            result = {
                'answer': answer,
                'context_chunks': [
                    {
                        'text': match['text'],
                        'score': match['score']
                    }
                    for match in matches
                ]
            }
            
            # Cache result
            cache.set(cache_key, result, timeout=3600)  # 1 hour
            
            logger.info(f"Generated answer for question: {question[:50]}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}", exc_info=True)
            raise