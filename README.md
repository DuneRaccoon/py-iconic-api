# Iconic API Client for Python

A Python client for interacting with the Iconic (SellerCenter) API.

## Features

- OAuth2 Client Credentials authentication with automatic token management.
- Synchronous and Asynchronous clients.
- Rate limiting respecting API guidelines.
- Request signing for secure endpoints.
- Pydantic models for type-safe API responses.
- Support for async testing with pytest-asyncio.
- Mocking HTTP requests with respx.
- Complete product set and product management.
- Support for hybrid product search and management.
- Product grouping functionality.

## Installation

```bash
pip install py-iconic-api
```

## Usage Examples

### Managing Products

```python
from iconic_api.client import IconicClient
from iconic_api.models import CreateProductRequest

# Initialize the client
client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.com"
)

# Get a list of products for a product set
products = client.product_sets.get_products(product_set_id=123)

# Add a new product to a product set
create_product_request = CreateProductRequest(
    seller_sku="EXAMPLE-SKU-001",
    variation="M",
    status="active",
    name="Example Product"
)
product = client.product_sets.create_product(123, create_product_request)

# Update product status
client.product_sets.update_product_status(product_set_id=123, product_id=456, status="inactive")

# Search for hybrid products
from iconic_api.models import SearchHybridRequest
hybrid_products = client.product_sets.search_hybrid(SearchHybridRequest(query="example product"))
```

See the `examples` directory for more detailed usage examples.