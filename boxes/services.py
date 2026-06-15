"""
Box selection service containing the core algorithm for recommending boxes.
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from .models import Box, Order, Product


class BoxSelectionService:
    """
    Service class that implements the box selection algorithm.
    
    Strategy:
    1. Filter boxes that can fit the total weight
    2. For single items: Check if dimensions fit
    3. For multiple items: Use volume-based heuristic with packing efficiency
    4. Return the cheapest suitable box
    """
    
    # Packing efficiency factor (accounts for wasted space when packing multiple items)
    PACKING_EFFICIENCY = 0.7  # Assume 70% space utilization for multiple items
    
    @classmethod
    def recommend_box_for_order(cls, order: Order) -> Optional[Box]:
        """
        Recommend the most suitable box for an order.
        
        Args:
            order: Order instance with items
            
        Returns:
            Recommended Box instance or None if no suitable box found
        """
        items = order.items.select_related('product').all()
        
        if not items:
            return None
        
        # Calculate total weight
        total_weight = order.total_weight()
        
        # Get all boxes that can handle the weight, ordered by cost
        suitable_boxes = Box.objects.filter(
            max_weight__gte=total_weight
        ).order_by('cost', 'length')
        
        if not suitable_boxes.exists():
            return None
        
        # Special case: single product, single quantity
        if len(items) == 1 and items[0].quantity == 1:
            return cls._find_box_for_single_item(items[0].product, suitable_boxes)
        
        # Special case: single product, multiple quantities (stackable)
        if len(items) == 1:
            return cls._find_box_for_stackable_items(
                items[0].product, 
                items[0].quantity, 
                suitable_boxes
            )
        
        # Multiple different products: use volume-based heuristic
        return cls._find_box_for_multiple_items(items, suitable_boxes)
    
    @classmethod
    def _find_box_for_single_item(cls, product: Product, suitable_boxes) -> Optional[Box]:
        """
        Find the cheapest box that can fit a single product.
        """
        for box in suitable_boxes:
            if box.can_fit_dimensions(product.length, product.width, product.height):
                return box
        return None
    
    @classmethod
    def _find_box_for_stackable_items(
        cls, 
        product: Product, 
        quantity: int, 
        suitable_boxes
    ) -> Optional[Box]:
        """
        Find box for multiple units of the same product.
        Tries stacking in different orientations.
        """
        for box in suitable_boxes:
            # Try stacking along each dimension
            if cls._can_stack_items(product, quantity, box):
                return box
        return None
    
    @classmethod
    def _can_stack_items(cls, product: Product, quantity: int, box: Box) -> bool:
        """
        Check if items can be stacked in the box in any orientation.
        """
        p_dims = [float(product.length), float(product.width), float(product.height)]
        b_dims = [float(box.length), float(box.width), float(box.height)]
        
        # Try stacking along each axis
        for stack_axis in range(3):
            for perm in cls._get_permutations([0, 1, 2]):
                # Check if we can fit 'quantity' items stacked along stack_axis
                dims_needed = p_dims.copy()
                dims_needed[perm[stack_axis]] *= quantity
                
                # Check if these dimensions fit in box
                product_sorted = sorted([dims_needed[perm[0]], dims_needed[perm[1]], dims_needed[perm[2]]])
                box_sorted = sorted(b_dims)
                
                if all(p <= b for p, b in zip(product_sorted, box_sorted)):
                    return True
        
        return False
    
    @classmethod
    def _find_box_for_multiple_items(cls, items, suitable_boxes) -> Optional[Box]:
        """
        Find box for multiple different products using volume heuristic.
        """
        # Calculate total volume needed (with packing efficiency factor)
        total_volume = sum(
            item.product.volume() * item.quantity 
            for item in items
        )
        required_volume = total_volume / cls.PACKING_EFFICIENCY
        
        # Find cheapest box with sufficient volume
        for box in suitable_boxes:
            if box.volume() >= required_volume:
                # Additional check: ensure largest item can fit
                if cls._largest_item_fits(items, box):
                    return box
        
        return None
    
    @classmethod
    def _largest_item_fits(cls, items, box: Box) -> bool:
        """
        Verify that the largest item in the order can fit in the box.
        """
        for item in items:
            product = item.product
            if not box.can_fit_dimensions(product.length, product.width, product.height):
                return False
        return True
    
    @staticmethod
    def _get_permutations(lst: List[int]) -> List[List[int]]:
        """Generate all permutations of a list."""
        if len(lst) <= 1:
            return [lst]
        
        result = []
        for i in range(len(lst)):
            rest = lst[:i] + lst[i+1:]
            for p in BoxSelectionService._get_permutations(rest):
                result.append([lst[i]] + p)
        return result
    
    @classmethod
    def get_recommendation_details(cls, order: Order) -> Dict[str, Any]:
        """
        Get detailed information about the box recommendation.
        
        Returns:
            Dictionary with recommendation details including reasoning
        """
        recommended_box = cls.recommend_box_for_order(order)
        
        items = order.items.select_related('product').all()
        total_weight = order.total_weight()
        total_volume = order.total_volume()
        
        result = {
            'order_number': order.order_number,
            'total_weight': float(total_weight),
            'total_volume': float(total_volume),
            'item_count': sum(item.quantity for item in items),
            'unique_products': items.count(),
            'recommended_box': None,
            'reasoning': '',
            'alternatives': []
        }
        
        if recommended_box:
            result['recommended_box'] = {
                'id': recommended_box.id,
                'name': recommended_box.name,
                'dimensions': {
                    'length': float(recommended_box.length),
                    'width': float(recommended_box.width),
                    'height': float(recommended_box.height),
                },
                'max_weight': float(recommended_box.max_weight),
                'cost': float(recommended_box.cost),
                'volume': recommended_box.volume(),
                'volume_utilization': (total_volume / recommended_box.volume() * 100) if recommended_box.volume() > 0 else 0
            }
            
            result['reasoning'] = cls._generate_reasoning(order, recommended_box, items)
            
            # Find alternative boxes (next 2 cheapest options)
            alternatives = Box.objects.filter(
                max_weight__gte=total_weight
            ).exclude(id=recommended_box.id).order_by('cost')[:2]
            
            result['alternatives'] = [
                {
                    'name': box.name,
                    'cost': float(box.cost),
                    'dimensions': f"{box.length}x{box.width}x{box.height}cm"
                }
                for box in alternatives
            ]
        else:
            result['reasoning'] = "No suitable box found. The order may be too heavy or too large for available boxes."
        
        return result
    
    @classmethod
    def _generate_reasoning(cls, order: Order, box: Box, items) -> str:
        """Generate human-readable reasoning for the recommendation."""
        total_weight = order.total_weight()
        total_volume = order.total_volume()
        
        reasons = []
        reasons.append(f"Selected '{box.name}' as the most cost-effective option at ${box.cost}.")
        reasons.append(f"Box can handle {box.max_weight}kg (order: {total_weight:.2f}kg).")
        
        utilization = (total_volume / box.volume() * 100) if box.volume() > 0 else 0
        reasons.append(f"Volume utilization: {utilization:.1f}%.")
        
        if len(items) == 1 and items[0].quantity == 1:
            reasons.append("Single item order - exact dimensional fit confirmed.")
        elif len(items) == 1:
            reasons.append(f"Stackable items ({items[0].quantity} units of same product).")
        else:
            reasons.append(f"Multiple products ({items.count()} different items) - volume-based selection with {cls.PACKING_EFFICIENCY*100}% packing efficiency.")
        
        return " ".join(reasons)
