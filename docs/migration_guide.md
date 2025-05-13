# Migration Guide: Moving to the Resource-Based API

This guide provides instructions for migrating from the previous API-module approach to the new resource-based architecture.

## Key Differences

The new resource-based API offers several advantages:

1. **Object-Oriented Approach**: Resources represent both collections and specific instances
2. **Intuitive Navigation**: Direct navigation between related resources
3. **Improved Pagination**: Built-in pagination support with multiple access patterns
4. **Better Type Safety**: More consistent type hints and model integration
5. **Enhanced Async Support**: Comprehensive async methods throughout

## Migration Steps

### 1. Client Initialization

**Old Approach**:
```python
from iconic_api.client import IconicClient

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.com"
)

# Accessing API modules
products = client.product_sets.get_products(product_set_id=123)
```

**New Approach**:
```python
from iconic_api.client import IconicClient

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.com"
)

# Accessing resource collections
products = client.product_sets.get(123).get_products()
# OR
product_set = client.product_sets.get(123)
products = product_set.get_products()
```

### 2. Working with Resources

#### Fetching Resources

**Old Approach**:
```python
# Get a product set
product_set = client.product_sets.get_product_set(123)

# Get a product
product = client.product_sets.get_product(product_set_id=123, product_id=456)
```

**New Approach**:
```python
# Get a product set
product_set = client.product_sets.get(123)

# Get a product (with navigation)
product = product_set.get_product(456)
# OR
product = client.products.get(456)  # If you know the product ID
```

#### Creating Resources

**Old Approach**:
```python
from iconic_api.models import CreateProductSetRequest, CreateProductRequest

# Create a product set
create_request = CreateProductSetRequest(
    name="Example Product Set",
    price=99.99,
    seller_sku="EXAMPLE-SKU-001",
    brand_id=123,
    primary_category_id=456,
    description="Example description",
    attributes={}
)
product_set = client.product_sets.create_product_set(create_request)

# Create a product
product_request = CreateProductRequest(
    seller_sku="EXAMPLE-PROD-001",
    variation="M",
    status="active",
    name="Example Product"
)
product = client.product_sets.create_product(product_set.id, product_request)
```

**New Approach**:
```python
from iconic_api.models import CreateProductSetRequest, CreateProductRequest

# Create a product set (supports both model and dict)
create_request = CreateProductSetRequest(
    name="Example Product Set",
    price=99.99,
    seller_sku="EXAMPLE-SKU-001",
    brand_id=123,
    primary_category_id=456,
    description="Example description",
    attributes={}
)
product_set = client.product_sets.create_product_set(create_request)
# OR with a dictionary
product_set = client.product_sets.create_product_set({
    "name": "Example Product Set",
    "price": 99.99,
    # ... other fields
})

# Create a product
product_request = CreateProductRequest(
    seller_sku="EXAMPLE-PROD-001",
    variation="M",
    status="active",
    name="Example Product"
)
product = product_set.create_product(product_request.model_dump())
# OR with a dictionary
product = product_set.create_product({
    "seller_sku": "EXAMPLE-PROD-001",
    "variation": "M",
    "status": "active",
    "name": "Example Product"
})
```

#### Updating Resources

**Old Approach**:
```python
from iconic_api.models import UpdateProductSetRequest, UpdateProductRequest

# Update a product set
update_request = UpdateProductSetRequest(
    name="Updated Product Set",
    description="Updated description"
)
updated_set = client.product_sets.update_product_set(123, update_request)

# Update a product
product_update = UpdateProductRequest(
    seller_sku="UPDATED-SKU-001",
    status="inactive"
)
updated_product = client.product_sets.update_product(123, 456, product_update)

# Update product status
client.product_sets.update_product_status(123, 456, "inactive")
```

**New Approach**:
```python
# Update a product set
product_set = client.product_sets.get(123)
updated_set = product_set.update_product_set({
    "name": "Updated Product Set",
    "description": "Updated description"
})

# Update a product
product = client.products.get(456)
# OR
product = product_set.get_product(456)

updated_product = product.update({
    "seller_sku": "UPDATED-SKU-001"
})

# Update product status
product.update_status("inactive")
```

### 3. Listing and Filtering

**Old Approach**:
```python
from iconic_api.models import ListProductSetsRequest

# List product sets
request = ListProductSetsRequest(
    status="active",
    brand_ids=[123],
    limit=10,
    offset=0
)
product_sets = client.product_sets.list_product_sets(request)
```

**New Approach**:
```python
# Using keyword arguments
product_sets = client.product_sets.list(
    status="active",
    brand_ids=[123],
    limit=10,
    offset=0
)

# Using request model (same as before)
from iconic_api.models import ListProductSetsRequest

request = ListProductSetsRequest(
    status="active",
    brand_ids=[123],
    limit=10,
    offset=0
)
product_sets = client.product_sets.list(**request.to_api_params())
```

### 4. Pagination

**Old Approach**:
```python
# Manual pagination
offset = 0
limit = 100
all_items = []

while True:
    request = ListProductSetsRequest(
        status="active",
        limit=limit,
        offset=offset
    )
    page = client.product_sets.list_product_sets(request)
    
    if not page.items:
        break
        
    all_items.extend(page.items)
    offset += limit
    
    if len(page.items) < limit:
        break
```

**New Approach**:
```python
# Simple pagination
paginated = client.product_sets.paginate(
    status="active",
    limit=100
)
print(f"Page 1: {len(paginated.items)} of {paginated.total_count} total")

# Get all items automatically
all_items = client.product_sets.paginate_all(status="active")
print(f"All items: {len(all_items)}")

# Using a generator for memory efficiency
for product_set in client.product_sets.paginate_generator(status="active"):
    # Process each product set one at a time
    print(f"Processing: {product_set.name}")
```

### 5. Async Operations

**Old Approach**:
```python
import asyncio
from iconic_api.client import IconicAsyncClient
from iconic_api.models import ListProductSetsRequest

async def get_data():
    client = IconicAsyncClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        instance_domain="your_instance.com"
    )
    
    # List product sets
    request = ListProductSetsRequest(
        status="active",
        limit=10
    )
    product_sets = await client.product_sets.list_product_sets_async(request)
    
    # Get product in a set
    product = await client.product_sets.get_product_async(123, 456)
    
    await client.close()
    return product_sets, product

product_sets, product = asyncio.run(get_data())
```

**New Approach**:
```python
import asyncio
from iconic_api.client import IconicAsyncClient

async def get_data():
    client = IconicAsyncClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        instance_domain="your_instance.com"
    )
    
    # List product sets
    product_sets = await client.product_sets.list_async(
        status="active",
        limit=10
    )
    
    # Get a product set
    product_set = await client.product_sets.get_async(123)
    
    # Get a product in the set
    product = await product_set.get_product_async(456)
    
    # Concurrently fetch related data
    brand_task = client.brands.get_async(product_set.brandId)
    products_task = product_set.get_products_async()
    
    brand, products = await asyncio.gather(brand_task, products_task)
    
    await client.close()
    return product_sets, product, brand, products

product_sets, product, brand, products = asyncio.run(get_data())
```

## Complete Examples

For complete examples of using the new resource-based API, see the following examples:

1. `examples/resource_based_example.py` - Basic usage
2. `examples/comprehensive_example.py` - Comprehensive examples of all features
