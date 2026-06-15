"""
Serializers for the box selection API.
"""
from rest_framework import serializers
from .models import Box, Product, Order, OrderItem


class BoxSerializer(serializers.ModelSerializer):
    """Serializer for Box model."""
    volume = serializers.SerializerMethodField()
    
    class Meta:
        model = Box
        fields = ['id', 'name', 'length', 'width', 'height', 'max_weight', 'cost', 'volume']
    
    def get_volume(self, obj):
        return obj.volume()


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    volume = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'length', 'width', 'height', 'weight', 'volume']
    
    def get_volume(self, obj):
        return obj.volume()


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    items = OrderItemSerializer(many=True)
    recommended_box = BoxSerializer(read_only=True)
    total_weight = serializers.SerializerMethodField()
    total_volume = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'created_at', 'items', 'recommended_box', 
                  'total_weight', 'total_volume']
        read_only_fields = ['created_at', 'recommended_box']
    
    def get_total_weight(self, obj):
        return obj.total_weight()
    
    def get_total_volume(self, obj):
        return obj.total_volume()
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class BoxRecommendationRequestSerializer(serializers.Serializer):
    """Serializer for box recommendation requests."""
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        min_length=1
    )
    
    def validate_items(self, value):
        """Validate that each item has required fields."""
        for item in value:
            if 'product_id' not in item:
                raise serializers.ValidationError("Each item must have a 'product_id'")
            if 'quantity' not in item:
                raise serializers.ValidationError("Each item must have a 'quantity'")
            
            # Validate quantity is positive integer
            try:
                qty = int(item['quantity'])
                if qty < 1:
                    raise ValueError()
                item['quantity'] = qty
            except (ValueError, TypeError):
                raise serializers.ValidationError("Quantity must be a positive integer")
            
            # Validate product exists
            try:
                product_id = int(item['product_id'])
                if not Product.objects.filter(id=product_id).exists():
                    raise serializers.ValidationError(f"Product with id {product_id} does not exist")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Invalid product_id")
        
        return value
