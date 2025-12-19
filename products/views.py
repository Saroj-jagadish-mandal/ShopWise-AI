
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from celery.result import AsyncResult
import uuid
import logging

from .models import Product, Review, ChatSession, ChatMessage
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer,
    ReviewSerializer, ChatSessionSerializer, ChatMessageSerializer,
    AskQuestionSerializer
)
from .tasks import scrape_and_embed_product
from .services import QAService

logger = logging.getLogger(__name__)


class ProductListCreateView(APIView):
    """
    Handles:
    - GET /products/ (List all products)
    - POST /products/ (Create/Scrape a product)
    """
    
    def get(self, request):
        # 1. Fetch Data (The QuerySet)
        queryset = Product.objects.all().order_by('-created_at')

        # 2. Manual Filtering
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(brand__icontains=search)
            )
        
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 3. Manual Pagination (Because APIView doesn't do it automatically)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(queryset, request)
        
        # 4. Serialization
        serializer = ProductListSerializer(result_page, many=True)

        # 5. Return Response (Paginated)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        # 1. Validate Input
        serializer = ProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        url = serializer.validated_data['url']

        # 2. Check Existence Logic
        existing_product = Product.objects.filter(url=url).first()
        if existing_product:
            if existing_product.status == 'completed':
                return Response({
                    'message': 'Product already exists',
                    'product': ProductDetailSerializer(existing_product).data
                }, status=status.HTTP_200_OK)
            elif existing_product.status in ['pending', 'scraping', 'embedding']:
                return Response({
                    'message': 'Product is being processed',
                    'product': ProductDetailSerializer(existing_product).data
                }, status=status.HTTP_200_OK)
        
        # 3. Create & Save
        product = Product.objects.create(url=url, status='pending')
        
        # 4. Trigger Celery Task
        task = scrape_and_embed_product.delay(str(product.id))
        product.task_id = task.id
        product.save()

        logger.info(f"Created product {product.id}...")

        return Response({
            'message': 'Product scraping started',
            'product': ProductDetailSerializer(product).data,
            'task_id': task.id
        }, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    """
    Handles:
    - GET /products/<id>/ (Retrieve one)
    - PUT /products/<id>/ (Update)
    - DELETE /products/<id>/ (Delete)
    """

    def get(self, request, id):
        product = get_object_or_404(Product, id=id)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)

    def put(self, request, id):
        product = get_object_or_404(Product, id=id)
        serializer = ProductDetailSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        product = get_object_or_404(Product, id=id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- 2. Custom Action Views (Using APIView) ---

class ProductStatusView(APIView):
    """
    Handles: GET /products/<id>/status/
    """
    def get(self, request, id):
        product = get_object_or_404(Product, id=id)
        
        response_data = {
            'product_id': str(product.id),
            'status': product.status,
            'task_id': product.task_id,
            'error_message': product.error_message
        }
        
        if product.task_id and product.status in ['pending', 'scraping', 'embedding']:
            task_result = AsyncResult(product.task_id)
            response_data['task_status'] = task_result.status
            response_data['task_info'] = str(task_result.info)
            
        return Response(response_data)


class ProductRetryView(APIView):
    """
    Handles: POST /products/<id>/retry/
    """
    def post(self, request, id):
        product = get_object_or_404(Product, id=id)
        
        if product.status != 'failed':
            return Response(
                {'error': 'Product is not in failed state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset and retry logic
        product.status = 'pending'
        product.error_message = None
        product.save()
        
        task = scrape_and_embed_product.delay(str(product.id))
        product.task_id = task.id
        product.save()
        
        return Response({
            'message': 'Scraping restarted',
            'task_id': task.id
        })


class ProductAskView(APIView):
    """
    Handles: POST /products/<id>/ask/
    """
    def post(self, request, id):
        product = get_object_or_404(Product, id=id)
        
        if product.status != 'completed':
            return Response(
                {'error': 'Product data is not ready yet'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = AskQuestionSerializer(data=request.data)
        if not serializer.is_valid():
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data['question']
        session_id = serializer.validated_data.get('session_id')
        
        # Session Logic
        if session_id:
            chat_session = ChatSession.objects.filter(
                session_id=session_id, product=product
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
            
        # Save User Msg
        ChatMessage.objects.create(
            session=chat_session, role='user', content=question
        )
        
        # Get Chat History
        chat_history = [
            {'role': msg.role, 'content': msg.content}
            for msg in chat_session.messages.all().order_by('created_at')[:10]
        ]
        
        # Call AI Service
        qa_service = QAService()
        try:
            result = qa_service.get_answer(product.id, question, chat_history)
            
            # Save AI Msg
            ChatMessage.objects.create(
                session=chat_session,
                role='assistant',
                content=result['answer'],
                context_chunks=result['context_chunks']
            )
            
            return Response({
                'answer': result['answer'],
                'session_id': session_id,
                'context_chunks': result['context_chunks']
            })
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to generate answer'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# --- 3. Nested Resource Views (Using APIView) ---

class ProductReviewsView(APIView):
    """
    Handles: GET /products/<id>/reviews/
    """
    def get(self, request, id):
        # Manual check if product exists (Generics usually do this implicitly)
        if not Product.objects.filter(id=id).exists():
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(product_id=id).order_by('-created_at')
        
        # Manual Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(reviews, request)
        
        serializer = ReviewSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductChatSessionsView(APIView):
    """
    Handles: GET /products/<id>/chat-sessions/
    """
    def get(self, request, id):
        if not Product.objects.filter(id=id).exists():
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        sessions = ChatSession.objects.filter(product_id=id).order_by('-created_at')
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class ChatSessionMessagesView(APIView):
    """
    Handles: GET /chat-sessions/<session_id>/messages/
    """
    def get(self, request, session_id):
        session = get_object_or_404(ChatSession, session_id=session_id)
        messages = session.messages.all().order_by('created_at')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)