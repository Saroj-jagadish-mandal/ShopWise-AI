# from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Review, QuestionAnswer, ChatSession, ChatMessage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'brand', 'current_price', 'status_badge',
        'vector_count', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'brand']
    search_fields = ['title', 'brand', 'url']
    readonly_fields = [
        'id', 'pinecone_namespace', 'vector_count',
        'task_id', 'scraped_at', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'url', 'title', 'brand')
        }),
        ('Pricing', {
            'fields': ('current_price', 'original_price', 'availability')
        }),
        ('Product Details', {
            'fields': ('features', 'specifications', 'categories', 'variants')
        }),
        ('Additional Info', {
            'fields': ('sales_rank', 'related_products', 'shipping_info')
        }),
        ('Scraping Status', {
            'fields': (
                'status', 'task_id', 'error_message',
                'scraped_at', 'created_at', 'updated_at'
            )
        }),
        ('Vector Database', {
            'fields': ('pinecone_namespace', 'vector_count')
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'scraping': 'blue',
            'embedding': 'purple',
            'completed': 'green',
            'failed': 'red'
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    actions = ['retry_scraping']
    
    def retry_scraping(self, request, queryset):
        from .tasks import scrape_and_embed_product
        
        count = 0
        for product in queryset.filter(status='failed'):
            product.status = 'pending'
            product.error_message = None
            product.save()
            
            task = scrape_and_embed_product.delay(str(product.id))
            product.task_id = task.id
            product.save()
            count += 1
        
        self.message_user(request, f'{count} products queued for retry')
    retry_scraping.short_description = 'Retry failed scraping'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer_name', 'rating', 'title', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['title', 'text', 'customer_name']
    readonly_fields = ['id', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ['product', 'question_preview', 'created_at']
    search_fields = ['question', 'answer']
    readonly_fields = ['id', 'created_at']
    
    def question_preview(self, obj):
        return obj.question[:100] + '...' if len(obj.question) > 100 else obj.question
    question_preview.short_description = 'Question'


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['role', 'content', 'created_at']
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'product', 'message_count', 'created_at']
    search_fields = ['session_id', 'product__title']
    readonly_fields = ['id', 'session_id', 'created_at', 'updated_at']
    inlines = [ChatMessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content']
    readonly_fields = ['id', 'created_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
