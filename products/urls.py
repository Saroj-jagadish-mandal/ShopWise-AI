from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ChatSessionViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'chat-sessions', ChatSessionViewSet, basename='chat-session')

urlpatterns = [
    path('', include(router.urls)),
]