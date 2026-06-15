"""
Admin configuration for boxes app.
"""
from django.contrib import admin
from .models import Box, Product, Order, OrderItem


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ['name', 'length', 'width', 'height', 'max_weight', 'cost', 'volume']
    list_filter = ['max_weight', 'cost']
    search_fields = ['name']
    
    def volume(self, obj):
        return f"{obj.volume():.2f} cm³"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'length', 'width', 'height', 'weight', 'volume']
    list_filter = ['weight']
    search_fields = ['name', 'sku']
    
    def volume(self, obj):
        return f"{obj.volume():.2f} cm³"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'created_at', 'recommended_box', 'total_weight', 'item_count']
    list_filter = ['created_at', 'recommended_box']
    search_fields = ['order_number']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at']
    
    def total_weight(self, obj):
        return f"{obj.total_weight():.2f} kg"
    
    def item_count(self, obj):
        return sum(item.quantity for item in obj.items.all())
