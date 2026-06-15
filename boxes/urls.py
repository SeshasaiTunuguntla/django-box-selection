"""
URL configuration for boxes app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoxViewSet, ProductViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'boxes', BoxViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
