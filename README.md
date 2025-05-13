# Iconic API Client for Python

A Python client for interacting with the Iconic (SellerCenter) API.

## Features

- OAuth2 Client Credentials authentication with automatic token management
- Both Synchronous and Asynchronous clients
- Resource-based API interaction with intuitive, object-oriented design
- Rate limiting respecting API guidelines
- Request signing for secure endpoints
- Pydantic models for type-safe API responses
- Support for async testing with pytest-asyncio
- Mocking HTTP requests with respx
- Complete product set and product management
- Support for hybrid product search and management
- Product grouping functionality

## Installation

```bash
pip install py-iconic-api
```

## Basic Usage

### Initialize the Client

```python
from iconic_api.client import IconicClient

# Initialize the client
client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.com"
)
```

### Resource-Based API

The client provides a resource-based interface that makes working with the API more intuitive and object-oriented:

```python
# Get a product set by ID
product_set = client.product_sets.get(123)

# Access properties directly
print(f"Product Set Name: {product_set.name}")

# Get all products within this product set
products = product_set.get_products()

# Update a product's status
product = products[0]
product.update_status("inactive")

# Create new products within the product set
new_product = product_set.create_product({
    "seller_sku": "EXAMPLE-SKU-001",
    "variation": "M",
    "status": "active",
    "name": "Example Product"
})
```

### Collection Operations

Resources can also be used as collections:

```python
# List all product sets with a filter
active_product_sets = client.product_sets.list(status="active")

# Search for product sets by brand
brand_products = client.product_sets.list(brand_ids=[123])

# Get a specific brand
brand = client.brands.get(123)

# Get all product sets for this brand
brand_product_sets = brand.get_product_sets()
```

### Pydantic Model Support

The client supports using both Pydantic models and dictionaries for input:

```python
from iconic_api.models import CreateProductSetRequest

# Using a Pydantic model
create_request = CreateProductSetRequest(
    name="Example Product Set",
    price=99.99,
    seller_sku="EXAMPLE-SKU-001",
    brand_id=123,
    primary_category_id=456,
    description="This is an example product set",
    attributes={}
)
product_set = client.product_sets.create_product_set(create_request)

# Using a dictionary
product_set = client.product_sets.create_product_set({
    "name": "Example Product Set",
    "price": 99.99,
    "seller_sku": "EXAMPLE-SKU-001",
    "brand_id": 123,
    "primary_category_id": 456,
    "description": "This is an example product set",
    "attributes": {}
})
```

### Async Support

The client also provides asynchronous support:

```python
import asyncio
from iconic_api.client import IconicAsyncClient

async def get_product_sets():
    client = IconicAsyncClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        instance_domain="your_instance.com"
    )
    
    # Get product sets asynchronously
    product_sets = await client.product_sets.list_async(status="active")
    
    # Get products for each product set concurrently
    tasks = [product_set.get_products_async() for product_set in product_sets]
    all_products = await asyncio.gather(*tasks)
    
    # Close the client when done
    await client.close()
    
    return product_sets, all_products

# Run with asyncio
product_sets, all_products = asyncio.run(get_product_sets())
```

## Advanced Examples

See the `examples` directory for more detailed usage examples, including:

- Managing product sets and products
- Working with orders
- Handling brands and categories
- Async API usage

## API Resources Available

- `client.product_sets` - Product set management
- `client.products` - Product management
- `client.brands` - Brand information
- `client.categories` - Category information
- `client.orders` - Order management
