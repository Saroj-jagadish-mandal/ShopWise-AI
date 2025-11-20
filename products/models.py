

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import uuid

class Product(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scraping', 'Scraping'),
        ('embedding', 'Embedding'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=500, unique=True)
    title = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    current_price = models.CharField(max_length=50, blank=True, null=True)
    original_price = models.CharField(max_length=50, blank=True, null=True)
    availability = models.CharField(max_length=255, blank=True, null=True)
    features = models.TextField(blank=True, null=True)
    specifications = models.JSONField(default=dict, blank=True)
    categories = models.JSONField(default=list, blank=True)
    variants = models.JSONField(default=list, blank=True)
    sales_rank = models.TextField(blank=True, null=True)
    related_products = models.JSONField(default=list, blank=True)
    shipping_info = models.JSONField(default=list, blank=True)
    
    # Vector database reference
    pinecone_namespace = models.CharField(max_length=100, blank=True, null=True)
    vector_count = models.IntegerField(default=0)
    
    # Scraping metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    task_id = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    scraped_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['url']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.title or self.url


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    title = models.TextField(blank=True, null=True)
    text = models.TextField()
    rating = models.CharField(max_length=20)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    helpful_votes = models.CharField(max_length=100, blank=True, null=True)
    review_date = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
        ]
    
    def __str__(self):
        return f"Review for {self.product.title} by {self.customer_name}"


class QuestionAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Q&A for {self.product.title}"


class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='chat_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chat session {self.session_id} for {self.product.title}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # Context used for this message
    context_chunks = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
    