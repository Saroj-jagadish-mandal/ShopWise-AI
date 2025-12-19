# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import ProductViewSet, ChatSessionViewSet

# router = DefaultRouter()
# router.register(r'products', ProductViewSet, basename='product')
# router.register(r'chat-sessions', ChatSessionViewSet, basename='chat-session')

# urlpatterns = [
#     path('', include(router.urls)),
# ]

from django.urls import path
from . import views

urlpatterns = [
    # 1. Product CRUD
    path('products/', views.ProductListCreateView.as_view(), name='product-list'),
    path('products/<uuid:id>/', views.ProductDetailView.as_view(), name='product-detail'),

    # 2. Product Actions (Previously @action)
    path('products/<uuid:id>/status/', views.ProductStatusView.as_view(), name='product-status'),
    path('products/<uuid:id>/retry/', views.ProductRetryView.as_view(), name='product-retry'),
    path('products/<uuid:id>/ask/', views.ProductAskView.as_view(), name='product-ask'),
    
    # 3. Nested Resources (Reviews & Sessions)
    path('products/<uuid:id>/reviews/', views.ProductReviewsView.as_view(), name='product-reviews'),
    path('products/<uuid:id>/chat-sessions/', views.ProductChatSessionsView.as_view(), name='product-sessions'),

    # 4. Standalone Chat Session URLs
    path('chat-sessions/<str:session_id>/messages/', views.ChatSessionMessagesView.as_view(), name='session-messages'),
]