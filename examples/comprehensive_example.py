#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comprehensive example script demonstrating the resource-based API client.
"""

import asyncio
import os
import time
from datetime import datetime, timedelta

from iconic_api.client import IconicClient, IconicAsyncClient
from iconic_api.models import (
    CreateProductSetRequest,
    CreateProductRequest,
    UpdateProductSetRequest,
    ListProductSetsRequest,
    ListBrandsRequest,
    ListOrdersRequest
)

CLIENT_ID = os.getenv("ICONIC_CLIENT_ID")
CLIENT_SECRET = os.getenv("ICONIC_CLIENT_SECRET")
INSTANCE_DOMAIN = os.getenv("ICONIC_INSTANCE_DOMAIN")


def resource_navigation_example():
    """Example demonstrating resource navigation from one resource to related resources."""
    client = IconicClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        instance_domain=INSTANCE_DOMAIN
    )
    
    try:
        # Get a product by seller SKU
        product = client.products.get_by_seller_sku("EXAMPLE-SKU-001")
        print(f"Found product: {product.name} (ID: {product.id})")
        
        # Navigate to its product set
        product_set = product.get_product_set()
        print(f"Product belongs to product set: {product_set.name} (ID: {product_set.id})")
        
        # Get the brand for this product set
        brand_id = product_set.brandId
        brand = client.brands.get(brand_id)
        print(f"Product set belongs to brand: {brand.name}")
        
        # Get all products in this product set
        products = product_set.get_products()
        print(f"Product set has {len(products)} products:")
        for p in products:
            print(f"  - {p.name} ({p.sellerSku}): {p.status}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


def pagination_example():
    """Example demonstrating pagination functionality."""
    client = IconicClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        instance_domain=INSTANCE_DOMAIN
    )
    
    try:
        # Get a paginated response
        paginated = client.product_sets.list(paginated=True, limit=10, status="active")
        print(f"Paginated results: {len(paginated.items)} items (page 1 of {paginated.total_count // paginated.limit + 1})")
        print(f"Total available: {paginated.total_count}")
        
        # Get the next page
        next_page = client.product_sets.paginate(limit=10, offset=10, status="active")
        print(f"Next page: {len(next_page.items)} items")
        
        # Get all results using automatic pagination
        all_items = list(client.product_sets.paginate(status="active", limit=50))
        print(f"All items: {len(all_items)}")
        
        # Use a generator to process items one by one
        print("Processing items one by one:")
        count = 0
        for product_set in client.product_sets.paginate(status="active", limit=10):
            count += 1
            print(f"  Processing product set: {product_set.name} ({count})")
            if count >= 5:  # Just to avoid printing too many
                print("  ...")
                break
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


def crud_operations_example():
    """Example demonstrating CRUD operations with the resource-based API."""
    client = IconicClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        instance_domain=INSTANCE_DOMAIN
    )
    
    try:
        # Create a new product set
        create_request = CreateProductSetRequest(
            name="Example Product Set",
            price=99.99,
            seller_sku="EXAMPLE-SKU-001",
            brand_id=123,  # Replace with an actual brand ID
            primary_category_id=456,  # Replace with an actual category ID
            description="This is an example product set",
            attributes={}  # Add required attributes based on the category
        )
        
        product_set = client.product_sets.create_product_set(create_request)
        print(f"Created product set: {product_set.name} (ID: {product_set.id})")
        
        # Update the product set
        updated_product_set = product_set.update_product_set({
            "name": f"{product_set.name} - Updated",
            "description": "This is an updated description"
        })
        print(f"Updated product set: {updated_product_set.name}")
        
        # Add a product to the product set
        product = product_set.create_product({
            "seller_sku": "EXAMPLE-PROD-001",
            "variation": "M",
            "status": "active",
            "name": "Example Product - Medium"
        })
        print(f"Created product: {product.name} (ID: {product.id})")
        
        # Update the product
        updated_product = product.update({
            "seller_sku": "EXAMPLE-PROD-001-UPDATED",
            "name": f"{product.name} - Updated"
        })
        print(f"Updated product: {updated_product.sellerSku}")
        
        # Update the product status
        product.update_status("inactive")
        print(f"Updated product status: {product.status}")
        
        # Get a specific product set by ID
        retrieved_product_set = client.product_sets.get(product_set.id)
        print(f"Retrieved product set: {retrieved_product_set.name}")
        
        # Get a specific product
        retrieved_product = product_set.get_product(product.id)
        print(f"Retrieved product: {retrieved_product.name}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


def filtering_example():
    """Example demonstrating filtering capabilities."""
    client = IconicClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        instance_domain=INSTANCE_DOMAIN
    )
    
    try:
        # Filter product sets by status
        active_product_sets = client.product_sets.list(status="active", limit=5)
        print(f"Active product sets (top 5): {len(active_product_sets)}")
        
        # Filter products by multiple attributes
        brand_id = 123  # Replace with an actual brand ID
        one_week_ago = datetime.now() - timedelta(days=7)
        
        # Using a request model
        request = ListProductSetsRequest(
            status="active",
            brand_ids=[brand_id],
            update_date_start=one_week_ago.date(),
            limit=10
        )
        
        recent_products = client.product_sets.list(
            status="active",
            brand_ids=[brand_id],
            update_date_start=one_week_ago.date(),
            limit=10
        )
        print(f"Recent active products for brand {brand_id}: {len(recent_products)}")
        
        # Filter brands by name
        brands = client.brands.list(name="example")
        print(f"Brands matching 'example': {len(brands)}")
        
        # Filter orders by date range
        one_month_ago = datetime.now() - timedelta(days=30)
        orders = client.orders.list(
            date_start=one_month_ago.date(),
            date_end=datetime.now().date(),
            limit=10
        )
        print(f"Orders in the last 30 days (top 10): {len(orders)}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


async def async_example():
    """Example demonstrating asynchronous operations."""
    client = IconicAsyncClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        instance_domain=INSTANCE_DOMAIN
    )
    
    try:
        # Get multiple resources concurrently
        product_sets_task = client.product_sets.list_async(status="active", limit=5)
        brands_task = client.brands.list_async(limit=5)
        categories_task = client.categories.list_async(limit=5)
        
        # Await all tasks concurrently
        product_sets, brands, categories = await asyncio.gather(
            product_sets_task,
            brands_task,
            categories_task
        )
        
        print(f"Async results - Product Sets: {len(product_sets)}, Brands: {len(brands)}, Categories: {len(categories)}")
        
        # Process items one by one asynchronously
        print("Processing items one by one asynchronously:")
        count = 0
        async for product_set in client.product_sets.paginate_async(status="active", limit=10):
            count += 1
            print(f"  Processing product set: {product_set.name} ({count})")
            if count >= 5:  # Just to avoid printing too many
                print("  ...")
                break
                
        # Create multiple resources concurrently
        if len(brands) > 0:
            brand_id = brands[0].id
            if len(categories) > 0:
                category_id = categories[0].id
                
                # Create multiple product sets concurrently
                create_tasks = []
                for i in range(3):
                    create_request = CreateProductSetRequest(
                        name=f"Async Product Set {i}",
                        price=99.99 + i,
                        seller_sku=f"ASYNC-SKU-00{i}",
                        brand_id=brand_id,
                        primary_category_id=category_id,
                        description=f"This is async product set {i}",
                        attributes={}
                    )
                    create_tasks.append(client.product_sets.create_product_set_async(create_request))
                
                created_product_sets = await asyncio.gather(*create_tasks)
                print(f"Created {len(created_product_sets)} product sets concurrently")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    print("\n--- Resource Navigation Example ---")
    resource_navigation_example()
    
    print("\n--- Pagination Example ---")
    pagination_example()
    
    print("\n--- CRUD Operations Example ---")
    crud_operations_example()
    
    print("\n--- Filtering Example ---")
    filtering_example()
    
    print("\n--- Async Example ---")
    asyncio.run(async_example())
