# from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import Q
from celery.result import AsyncResult
import uuid
import logging

from .models import Product, Review, ChatSession, ChatMessage
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer,
    ReviewSerializer, ChatSessionSerializer, ChatMessageSerializer,
    AskQuestionSerializer, QuestionResponseSerializer
)
from .tasks import scrape_and_embed_product
from .services import QAService

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations
    """
    queryset = Product.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        """Filter products based on query params"""
        queryset = super().get_queryset()
        
        # Search by title or brand
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(brand__icontains=search)
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create a new product and start scraping"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        url = serializer.validated_data['url']
        
        # Check if product already exists
        existing_product = Product.objects.filter(url=url).first()
        if existing_product:
            if existing_product.status == 'completed':
                return Response(
                    {
                        'message': 'Product already exists',
                        'product': ProductDetailSerializer(existing_product).data
                    },
                    status=status.HTTP_200_OK
                )
            elif existing_product.status in ['pending', 'scraping', 'embedding']:
                return Response(
                    {
                        'message': 'Product is being processed',
                        'product': ProductDetailSerializer(existing_product).data
                    },
                    status=status.HTTP_200_OK
                )
        
        # Create product
        product = Product.objects.create(url=url, status='pending')
        
        # Start scraping task
        task = scrape_and_embed_product.delay(str(product.id))
        product.task_id = task.id
        product.save()
        
        logger.info(f"Created product {product.id} and started scraping task {task.id}")
        
        return Response(
            {
                'message': 'Product scraping started',
                'product': ProductDetailSerializer(product).data,
                'task_id': task.id
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get scraping status"""
        product = self.get_object()
        
        response_data = {
            'product_id': str(product.id),
            'status': product.status,
            'task_id': product.task_id,
            'error_message': product.error_message
        }
        
        # If task is running, get Celery task status
        if product.task_id and product.status in ['pending', 'scraping', 'embedding']:
            task_result = AsyncResult(product.task_id)
            response_data['task_status'] = task_result.status
            response_data['task_info'] = str(task_result.info)
        
        return Response(response_data)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry failed scraping"""
        product = self.get_object()
        
        if product.status != 'failed':
            return Response(
                {'error': 'Product is not in failed state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset status and start new task
        product.status = 'pending'
        product.error_message = None
        product.save()
        
        task = scrape_and_embed_product.delay(str(product.id))
        product.task_id = task.id
        product.save()
        
        return Response(
            {
                'message': 'Scraping restarted',
                'task_id': task.id
            }
        )
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get product reviews"""
        product = self.get_object()
        reviews = product.reviews.all()
        
        # Pagination
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ask(self, request, pk=None):
        """Ask a question about the product"""
        product = self.get_object()
        
        # Validate product status
        if product.status != 'completed':
            return Response(
                {'error': 'Product data is not ready yet'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        question = serializer.validated_data['question']
        session_id = serializer.validated_data.get('session_id')
        
        # Get or create chat session
        if session_id:
            chat_session = ChatSession.objects.filter(
                session_id=session_id,
                product=product
            ).first()
        else:
            session_id = str(uuid.uuid4())
            chat_session = None
        
        if not chat_session:
            chat_session = ChatSession.objects.create(
                product=product,
                session_id=session_id,
                user=request.user if request.user.is_authenticated else None
            )
        
        # Save user message
        ChatMessage.objects.create(
            session=chat_session,
            role='user',
            content=question
        )
        
        # Get chat history
        chat_history = [
            {
                'role': msg.role,
                'content': msg.content
            }
            for msg in chat_session.messages.all()[:10]
        ]
        
        # Get answer using QA service
        qa_service = QAService()
        try:
            result = qa_service.get_answer(
                product_id=product.id,
                question=question,
                chat_history=chat_history
            )
            
            # Save assistant message
            ChatMessage.objects.create(
                session=chat_session,
                role='assistant',
                content=result['answer'],
                context_chunks=result['context_chunks']
            )
            
            response_data = {
                'answer': result['answer'],
                'session_id': session_id,
                'context_chunks': result['context_chunks']
            }
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to generate answer'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def chat_sessions(self, request, pk=None):
        """Get all chat sessions for a product"""
        product = self.get_object()
        sessions = product.chat_sessions.all()
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], url_path='chat_sessions/(?P<session_id>[^/.]+)')
    def delete_chat_session(self, request, pk=None, session_id=None):
        """Delete a chat session"""
        product = self.get_object()
        chat_session = get_object_or_404(
            ChatSession,
            product=product,
            session_id=session_id
        )
        chat_session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Chat Sessions
    """
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    lookup_field = 'session_id'
    
    @action(detail=True, methods=['get'])
    def messages(self, request, session_id=None):
        """Get all messages in a session"""
        session = self.get_object()
        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
