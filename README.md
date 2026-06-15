# AI-Assisted Box Selection System

A Django-based system that recommends the most suitable shipping box for e-commerce orders based on product dimensions, weight, and box capacity.

## Features

- **Smart Box Selection Algorithm**: Automatically recommends the most cost-effective box
- **Multiple Selection Strategies**:
  - Single item: Exact dimensional fit with rotation support
  - Stackable items: Optimized stacking for multiple units of same product
  - Multiple products: Volume-based heuristic with packing efficiency
- **RESTful API**: Complete CRUD operations for boxes, products, and orders
- **Comprehensive Testing**: 31 test cases covering models, services, and API endpoints
- **Admin Interface**: Django admin for easy data management
- **Sample Data**: Pre-configured boxes and products for testing

## System Requirements

- Python 3.8+
- Django 6.0+
- Django REST Framework 3.17+

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd django-assignment
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django djangorestframework
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Load sample data** (optional but recommended)
   ```bash
   python manage.py populate_sample_data
   ```

6. **Create superuser** (for admin access)
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Boxes
- `GET /api/boxes/` - List all boxes
- `POST /api/boxes/` - Create a new box
- `GET /api/boxes/{id}/` - Get box details
- `PUT /api/boxes/{id}/` - Update a box
- `DELETE /api/boxes/{id}/` - Delete a box

### Products
- `GET /api/products/` - List all products
- `POST /api/products/` - Create a new product
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update a product
- `DELETE /api/products/{id}/` - Delete a product

### Orders
- `GET /api/orders/` - List all orders
- `POST /api/orders/` - Create order (auto-calculates recommended box)
- `GET /api/orders/{id}/` - Get order details
- `POST /api/orders/recommend_box/` - Get box recommendation without creating order
- `POST /api/orders/{id}/calculate_box/` - Calculate box for existing order

## Usage Examples

### 1. Get Box Recommendation (without creating order)

```bash
curl -X POST http://localhost:8000/api/orders/recommend_box/ \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ]
  }'
```

Response:
```json
{
  "order_number": "TEMP-abc123",
  "total_weight": 2.4,
  "total_volume": 1250.0,
  "item_count": 3,
  "unique_products": 2,
  "recommended_box": {
    "id": 2,
    "name": "Medium Box",
    "dimensions": {
      "length": 40.0,
      "width": 30.0,
      "height": 20.0
    },
    "max_weight": 5.0,
    "cost": 3.0,
    "volume": 24000.0,
    "volume_utilization": 5.21
  },
  "reasoning": "Selected 'Medium Box' as the most cost-effective option at $3.0. Box can handle 5.0kg (order: 2.40kg). Volume utilization: 5.2%. Multiple products (2 different items) - volume-based selection with 70.0% packing efficiency.",
  "alternatives": [
    {
      "name": "Large Box",
      "cost": 5.5,
      "dimensions": "60.0x40.0x30.0cm"
    }
  ]
}
```

### 2. Create Order with Automatic Box Recommendation

```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD-12345",
    "items": [
      {"product_id": 1, "quantity": 1}
    ]
  }'
```

### 3. Create a New Box

```bash
curl -X POST http://localhost:8000/api/boxes/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Box",
    "length": "50.00",
    "width": "35.00",
    "height": "25.00",
    "max_weight": "7.50",
    "cost": "4.25"
  }'
```

### 4. Create a New Product

```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Console",
    "sku": "CONSOLE-001",
    "length": "30.00",
    "width": "25.00",
    "height": "10.00",
    "weight": "3.50"
  }'
```

## Box Selection Algorithm

The system uses a multi-strategy approach:

### 1. Single Item Orders
- Checks if product dimensions fit in available boxes (considering all rotations)
- Returns the cheapest box that fits

### 2. Stackable Items (Multiple units of same product)
- Tries stacking items along different axes
- Finds optimal orientation for space efficiency
- Returns cheapest suitable box

### 3. Multiple Different Products
- Uses volume-based heuristic with 70% packing efficiency factor
- Ensures all individual items can fit
- Prioritizes cost-effectiveness

### Weight Constraint
All strategies filter boxes by weight capacity first.

## Running Tests

Run the complete test suite:

```bash
python manage.py test boxes
```

Run specific test class:

```bash
python manage.py test boxes.tests.BoxSelectionServiceTest
```

Run with verbosity:

```bash
python manage.py test boxes -v 2
```

## Test Coverage

The test suite includes:
- **Model Tests**: 18 tests for Box, Product, Order models
- **Service Tests**: 8 tests for BoxSelectionService algorithm
- **API Tests**: 10 tests for REST endpoints
- **Edge Cases**: 3 tests for corner scenarios

Total: **31 test cases**

## Project Structure

```
django-assignment/
├── box_selection_system/      # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── boxes/                      # Main application
│   ├── models.py              # Box, Product, Order models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── services.py            # Box selection algorithm
│   ├── admin.py               # Admin configuration
│   ├── tests.py               # Test suite
│   ├── urls.py                # App URLs
│   └── management/
│       └── commands/
│           └── populate_sample_data.py
├── manage.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/`

Features:
- Manage boxes, products, and orders
- View calculated volumes and weights
- Filter and search functionality

## Sample Data

The `populate_sample_data` command creates:

**5 Boxes:**
- Small Box (20×15×10 cm, 2kg, $1.50)
- Medium Box (40×30×20 cm, 5kg, $3.00)
- Large Box (60×40×30 cm, 10kg, $5.50)
- Extra Large Box (80×60×40 cm, 20kg, $8.00)
- Flat Box (50×40×5 cm, 3kg, $2.00)

**10 Products:**
- Smartphone, Laptop, Monitor, Keyboard, Mouse
- Tablet, Headphones, External Hard Drive, USB Cable, Power Bank

## Design Decisions

1. **Decimal Fields**: Used for precise measurements (avoiding floating-point errors)
2. **Dimension Rotation**: Boxes can accommodate products in any orientation
3. **Packing Efficiency**: 70% factor for multiple items (industry standard)
4. **Cost Optimization**: Always selects cheapest suitable box
5. **Volume + Dimension Check**: Ensures both volume AND individual items fit
6. **Temporary Orders**: Recommendation endpoint doesn't persist data

## Limitations & Future Enhancements

**Current Limitations:**
- Simple volume-based packing for multiple items
- Doesn't account for fragility or stacking restrictions
- No 3D bin-packing optimization

**Potential Enhancements:**
- Advanced 3D bin-packing algorithms
- Product compatibility rules (fragile, stackable, etc.)
- Multi-box recommendations for large orders
- Shipping cost integration
- Machine learning for packing efficiency prediction

## License

This project is for educational/assessment purposes.

## Author

Developed as part of a Python/Django hiring assignment with AI assistance (see AI_USAGE.md for details).
