"""
Management command to populate the database with sample data.
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from boxes.models import Box, Product


class Command(BaseCommand):
    help = 'Populate the database with sample boxes and products'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample boxes...')
        
        boxes = [
            {
                'name': 'Small Box',
                'length': Decimal('20.00'),
                'width': Decimal('15.00'),
                'height': Decimal('10.00'),
                'max_weight': Decimal('2.00'),
                'cost': Decimal('1.50')
            },
            {
                'name': 'Medium Box',
                'length': Decimal('40.00'),
                'width': Decimal('30.00'),
                'height': Decimal('20.00'),
                'max_weight': Decimal('5.00'),
                'cost': Decimal('3.00')
            },
            {
                'name': 'Large Box',
                'length': Decimal('60.00'),
                'width': Decimal('40.00'),
                'height': Decimal('30.00'),
                'max_weight': Decimal('10.00'),
                'cost': Decimal('5.50')
            },
            {
                'name': 'Extra Large Box',
                'length': Decimal('80.00'),
                'width': Decimal('60.00'),
                'height': Decimal('40.00'),
                'max_weight': Decimal('20.00'),
                'cost': Decimal('8.00')
            },
            {
                'name': 'Flat Box',
                'length': Decimal('50.00'),
                'width': Decimal('40.00'),
                'height': Decimal('5.00'),
                'max_weight': Decimal('3.00'),
                'cost': Decimal('2.00')
            },
        ]
        
        for box_data in boxes:
            box, created = Box.objects.get_or_create(
                name=box_data['name'],
                defaults=box_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created box: {box.name}'))
            else:
                self.stdout.write(f'Box already exists: {box.name}')
        
        self.stdout.write('\nCreating sample products...')
        
        products = [
            {
                'name': 'Smartphone',
                'sku': 'PHONE-001',
                'length': Decimal('15.00'),
                'width': Decimal('8.00'),
                'height': Decimal('1.00'),
                'weight': Decimal('0.20')
            },
            {
                'name': 'Laptop',
                'sku': 'LAPTOP-001',
                'length': Decimal('35.00'),
                'width': Decimal('25.00'),
                'height': Decimal('2.50'),
                'weight': Decimal('2.00')
            },
            {
                'name': 'Monitor',
                'sku': 'MONITOR-001',
                'length': Decimal('55.00'),
                'width': Decimal('35.00'),
                'height': Decimal('8.00'),
                'weight': Decimal('4.50')
            },
            {
                'name': 'Keyboard',
                'sku': 'KEYB-001',
                'length': Decimal('45.00'),
                'width': Decimal('15.00'),
                'height': Decimal('3.00'),
                'weight': Decimal('0.80')
            },
            {
                'name': 'Mouse',
                'sku': 'MOUSE-001',
                'length': Decimal('10.00'),
                'width': Decimal('6.00'),
                'height': Decimal('4.00'),
                'weight': Decimal('0.10')
            },
            {
                'name': 'Tablet',
                'sku': 'TABLET-001',
                'length': Decimal('25.00'),
                'width': Decimal('18.00'),
                'height': Decimal('0.80'),
                'weight': Decimal('0.50')
            },
            {
                'name': 'Headphones',
                'sku': 'HEADP-001',
                'length': Decimal('20.00'),
                'width': Decimal('18.00'),
                'height': Decimal('8.00'),
                'weight': Decimal('0.30')
            },
            {
                'name': 'External Hard Drive',
                'sku': 'HDD-001',
                'length': Decimal('12.00'),
                'width': Decimal('8.00'),
                'height': Decimal('2.00'),
                'weight': Decimal('0.25')
            },
            {
                'name': 'USB Cable',
                'sku': 'CABLE-001',
                'length': Decimal('15.00'),
                'width': Decimal('10.00'),
                'height': Decimal('2.00'),
                'weight': Decimal('0.05')
            },
            {
                'name': 'Power Bank',
                'sku': 'PBANK-001',
                'length': Decimal('14.00'),
                'width': Decimal('7.00'),
                'height': Decimal('2.00'),
                'weight': Decimal('0.35')
            },
        ]
        
        for product_data in products:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
            else:
                self.stdout.write(f'Product already exists: {product.name}')
        
        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS('Sample data population complete!'))
        self.stdout.write(f'Total boxes: {Box.objects.count()}')
        self.stdout.write(f'Total products: {Product.objects.count()}')
