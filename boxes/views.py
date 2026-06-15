"""
API views for box selection system.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import Box, Product, Order, OrderItem
from .serializers import (
    BoxSerializer, 
    ProductSerializer, 
    OrderSerializer,
    BoxRecommendationRequestSerializer
)
from .services import BoxSelectionService


class BoxViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing boxes.
    """
    queryset = Box.objects.all()
    serializer_class = BoxSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    @action(detail=False, methods=['post'])
    def recommend_box(self, request):
        """
        Endpoint to get box recommendation without creating an order.
        
        POST /api/orders/recommend_box/
        {
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1}
            ]
        }
        """
        serializer = BoxRecommendationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create a temporary order for recommendation
        with transaction.atomic():
            # Use a temporary order number
            import uuid
            temp_order_number = f"TEMP-{uuid.uuid4().hex[:8]}"
            
            temp_order = Order.objects.create(order_number=temp_order_number)
            
            for item_data in serializer.validated_data['items']:
                product = Product.objects.get(id=item_data['product_id'])
                OrderItem.objects.create(
                    order=temp_order,
                    product=product,
                    quantity=item_data['quantity']
                )
            
            # Get recommendation details
            recommendation = BoxSelectionService.get_recommendation_details(temp_order)
            
            # Rollback the temporary order
            transaction.set_rollback(True)
        
        return Response(recommendation, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def calculate_box(self, request, pk=None):
        """
        Calculate and assign recommended box for an existing order.
        
        POST /api/orders/{id}/calculate_box/
        """
        order = self.get_object()
        
        recommended_box = BoxSelectionService.recommend_box_for_order(order)
        
        if recommended_box:
            order.recommended_box = recommended_box
            order.save()
            
            recommendation = BoxSelectionService.get_recommendation_details(order)
            
            return Response({
                'success': True,
                'message': f'Box "{recommended_box.name}" recommended for order {order.order_number}',
                'recommendation': recommendation
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'No suitable box found for this order'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        """
        Create an order and automatically calculate recommended box.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order = serializer.save()
        
        # Automatically calculate recommended box
        recommended_box = BoxSelectionService.recommend_box_for_order(order)
        if recommended_box:
            order.recommended_box = recommended_box
            order.save()
        
        # Return order with recommendation details
        order_serializer = self.get_serializer(order)
        recommendation = BoxSelectionService.get_recommendation_details(order)
        
        return Response({
            'order': order_serializer.data,
            'recommendation': recommendation
        }, status=status.HTTP_201_CREATED)
