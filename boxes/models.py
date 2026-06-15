from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Box(models.Model):
    """
    Represents a shipping box with dimensions, weight capacity, and cost.
    """
    name = models.CharField(max_length=100, unique=True)
    length = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal length in cm"
    )
    width = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal width in cm"
    )
    height = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal height in cm"
    )
    max_weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Maximum weight capacity in kg"
    )
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Box cost in currency units"
    )
    
    class Meta:
        verbose_name_plural = "Boxes"
        ordering = ['cost', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.length}x{self.width}x{self.height}cm, max {self.max_weight}kg)"
    
    def volume(self):
        """Calculate internal volume of the box."""
        return float(self.length * self.width * self.height)
    
    def can_fit_dimensions(self, length, width, height):
        """
        Check if given dimensions can fit in this box.
        Tries all possible orientations.
        """
        product_dims = sorted([float(length), float(width), float(height)])
        box_dims = sorted([float(self.length), float(self.width), float(self.height)])
        
        return all(p <= b for p, b in zip(product_dims, box_dims))
    
    def can_fit_weight(self, weight):
        """Check if given weight is within capacity."""
        return float(weight) <= float(self.max_weight)


class Product(models.Model):
    """
    Represents a product with dimensions and weight.
    """
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True)
    length = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Length in cm"
    )
    width = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Width in cm"
    )
    height = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Height in cm"
    )
    weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Weight in kg"
    )
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def volume(self):
        """Calculate volume of the product."""
        return float(self.length * self.width * self.height)


class Order(models.Model):
    """
    Represents a customer order containing multiple products.
    """
    order_number = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    recommended_box = models.ForeignKey(
        Box, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def total_weight(self):
        """Calculate total weight of all products in the order."""
        return sum(
            float(item.product.weight) * item.quantity 
            for item in self.items.all()
        )
    
    def total_volume(self):
        """Calculate total volume of all products in the order."""
        return sum(
            item.product.volume() * item.quantity 
            for item in self.items.all()
        )


class OrderItem(models.Model):
    """
    Represents a product within an order with quantity.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    class Meta:
        unique_together = ['order', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.order.order_number}"
