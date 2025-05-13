#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script showing how to use the new resource-based API client.
"""

import asyncio
import os
from dotenv import load_dotenv

from iconic_api.client import IconicClient, IconicAsyncClient
from iconic_api.models import (
    CreateProductSetRequest,
    CreateProductRequest,
    UpdateProductRequest,
    ProductGroupRequest,
    SearchHybridRequest,
    CreateProductBySinRequest
)

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("ICONIC_CLIENT_ID")
CLIENT_SECRET = os.getenv("ICONIC_CLIENT_SECRET")
INSTANCE_DOMAIN = os.getenv("ICONIC_INSTANCE_DOMAIN")


def sync_example():
    """Example using the synchronous client with the new resource-based API."""
    # Initialize the client
    client = IconicClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        instance_domain=INSTANCE_DOMAIN
    )

    try:
        # Create a new product set
        create_product_set_request = CreateProductSetRequest(
            name="Example Product Set",
            price=99.99,
            seller_sku="EXAMPLE-SKU-001",
            brand_id=123,  # Replace with an actual brand ID
            primary_category_id=456,  # Replace with an actual category ID
            description="This is an example product set",
            attributes={}  # Add required attributes based on the category
        )
        
        # Using the new resource-based API
        product_set = client.product_sets.create_product_set(create_product_set_request)
        print(f"Created product set with ID: {product_set.id}")
        
        # Add a product to the product set
        create_product_request = CreateProductRequest(
            seller_sku="EXAMPLE-PROD-001",
            variation="M",
            status="active",
            name="Example Product - Medium",
            product_identifier="123456789012"
        )
        
        # Create a product directly on the product set instance
        product = product_set.create_product(create_product_request.model_dump())
        print(f"Created product with ID: {product.id}")
        
        # Update the product
        updated_product = product.update_status("active")
        print(f"Updated product status: {product.status}")
        
        # Get products for the product set
        products = product_set.get_products()
        print(f"Found {len(products)} products in the product set")
        
        # Add the product set to a group
        group_request = ProductGroupRequest(name="Example Group")
        product_set.add_to_group(group_request)
        print("Added product set to group")
        
        # Get the product group
        group = product_set.get_group()
        print(f"Product set belongs to group: {group.get('name')}")
        
        # Remove from the group
        product_set.remove_from_group()
        print("Removed product set from group")
        
        # Search for hybrid products
        hybrid_search = SearchHybridRequest(query="example product")
        hybrid_products = client.product_sets.search_hybrid(hybrid_search)
        print(f"Found {len(hybrid_products)} hybrid products")
        
        # Get a list of brands
        brands = client.brands.list()
        print(f"Found {len(brands)} brands")
        
        # Get a category by ID
        category = client.categories.get(456)  # Replace with an actual category ID
        print(f"Category name: {category.name}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


async def async_example():
    """Example using the asynchronous client with the new resource-based API."""
    # Initialize the async client
    client = IconicAsyncClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        instance_domain=INSTANCE_DOMAIN
    )

    try:
        # Create a new product set
        create_product_set_request = CreateProductSetRequest(
            name="Async Example Product Set",
            price=129.99,
            seller_sku="ASYNC-SKU-001",
            brand_id=123,  # Replace with an actual brand ID
            primary_category_id=456,  # Replace with an actual category ID
            description="This is an async example product set",
            attributes={}  # Add required attributes based on the category
        )
        
        # Using the new resource-based API
        product_set = await client.product_sets.create_product_set_async(create_product_set_request)
        print(f"Created product set with ID: {product_set.id}")
        
        # Add a product to the product set
        create_product_request = CreateProductRequest(
            seller_sku="ASYNC-PROD-001",
            variation="L",
            status="active",
            name="Async Example Product - Large",
            product_identifier="987654321098"
        )
        
        # Create a product directly on the product set instance
        product = await product_set.create_product_async(create_product_request.model_dump())
        print(f"Created product with ID: {product.id}")
        
        # Get the product
        retrieved_product = await product_set.get_product_async(product.id)
        print(f"Retrieved product: {retrieved_product.sellerSku}")
        
        # Create a product by SIN
        sin_request = CreateProductBySinRequest(sin="EXAMPLE-SIN-123")
        try:
            result = await client.product_sets.create_product_by_sin_async(sin_request)
            print(f"Created product set by SIN with ID: {result.get('productSetId')}")
        except Exception as e:
            print(f"Error creating product by SIN: {e}")
            
        # Get a list of categories
        categories = await client.categories.list_async()
        print(f"Found {len(categories)} categories")
        
        # Get a brand by ID
        brand = await client.brands.get_async(123)  # Replace with an actual brand ID
        print(f"Brand name: {brand.name}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    print("Running synchronous example...")
    sync_example()
    
    print("\nRunning asynchronous example...")
    asyncio.run(async_example())
