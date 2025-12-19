from rest_framework import serializers
from .models import Product, Review, QuestionAnswer, ChatSession, ChatMessage


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id', 'title', 'text', 'rating', 
            'customer_name', 'helpful_votes', 'created_at'
        ]


class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = ['id', 'question', 'answer', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view"""
    class Meta:
        model = Product
        fields = [
            'id', 'url', 'title', 'brand', 'current_price',
            'status', 'created_at', 'updated_at'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail view"""
    reviews = ReviewSerializer(many=True, read_only=True)
    questions = QuestionAnswerSerializer(many=True, read_only=True)
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'url', 'title', 'brand', 'current_price', 'original_price',
            'availability', 'features', 'specifications', 'categories',
            'variants', 'sales_rank', 'related_products', 'shipping_info',
            'status', 'task_id', 'error_message', 'scraped_at',
            'vector_count', 'created_at', 'updated_at',
            'reviews', 'questions', 'review_count'
        ]
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a product"""
    class Meta:
        model = Product
        fields = ['url']
    
    def validate_url(self, value):
        """Validate Amazon URL"""
        if 'amazon.com' not in value and 'amazon.in' not in value:
            raise serializers.ValidationError(
                "Please provide a valid Amazon product URL"
            )
        return value


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'session_id', 'product', 'created_at', 
            'updated_at', 'messages', 'message_count'
        ]
    
    def get_message_count(self, obj):
        return obj.messages.count()


class AskQuestionSerializer(serializers.Serializer):
    """Serializer for asking a question"""
    question = serializers.CharField(max_length=1000)
    session_id = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True 
    )


class QuestionResponseSerializer(serializers.Serializer):
    """Serializer for question response"""
    answer = serializers.CharField()
    session_id = serializers.CharField()
    context_chunks = serializers.ListField(child=serializers.DictField())
