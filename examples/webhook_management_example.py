#!/usr/bin/env python3
"""
Comprehensive example showing how to use the Webhook resource in the Iconic API client.

This example demonstrates:
- Getting available webhook entities and events
- Creating webhooks
- Updating webhooks
- Managing webhook status
- Listing webhooks
- Working with webhook callbacks
- Deleting webhooks
"""

import asyncio
from typing import List, Dict, Any

from iconic_api import IconicClient, IconicAsyncClient
from iconic_api.models.webhook import WebhookEventAlias


def webhook_management_example():
    """Example of managing webhooks with the synchronous client."""
    
    # Initialize the client
    client = IconicClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        instance_domain="your-instance.theiconic.com.au"
    )
    
    try:
        # 1. Get available webhook entities and events
        print("=== Getting Available Webhook Entities ===")
        entities = client.webhooks.get_entities()
        print(f"Found {len(entities.events)} entity types:")
        for entity in entities.events:
            print(f"  - {entity.name}: {len(entity.events)} events")
            for event in entity.events:
                print(f"    * {event.name} ({event.alias})")
        
        # 2. Create a new webhook
        print("\n=== Creating a New Webhook ===")
        callback_url = "https://your-app.com/webhooks/iconic"
        events_to_subscribe = [
            WebhookEventAlias.ORDER_CREATED,
            WebhookEventAlias.ORDER_ITEMS_STATUS_CHANGED,
            WebhookEventAlias.PRODUCT_CREATED,
            WebhookEventAlias.PRODUCT_UPDATED
        ]
        
        webhook_response = client.webhooks.create_webhook(
            callback_url=callback_url,
            events=events_to_subscribe
        )
        print(f"Created webhook with ID: {webhook_response.webhook_id}")
        print(f"Created at: {webhook_response.created_at}")
        
        webhook_id = webhook_response.webhook_id
        
        # 3. List all webhooks
        print("\n=== Listing All Webhooks ===")
        webhooks_list = client.webhooks.list_webhooks()
        print(f"Found {len(webhooks_list.items)} webhooks:")
        for webhook in webhooks_list.items:
            print(f"  - ID: {webhook.id}, URL: {webhook.url}, Status: {webhook.status}")
        
        # 4. Update the webhook
        print("\n=== Updating Webhook ===")
        updated_events = [
            WebhookEventAlias.ORDER_CREATED,
            WebhookEventAlias.ORDER_ITEMS_STATUS_CHANGED,
            WebhookEventAlias.PRODUCT_CREATED,
            WebhookEventAlias.PRODUCT_UPDATED,
            WebhookEventAlias.STATISTICS_UPDATED
        ]
        
        updated_webhook = client.webhooks.update_webhook(
            webhook_uuid=webhook_id,
            callback_url=callback_url,
            events=updated_events
        )
        print(f"Updated webhook {updated_webhook.webhook_id} at {updated_webhook.updated_at}")
        
        # 5. Enable/disable webhook
        print("\n=== Managing Webhook Status ===")
        # Disable the webhook
        client.webhooks.update_webhook_status(webhook_id, is_enabled=False)
        print("Webhook disabled")
        
        # Re-enable the webhook
        client.webhooks.update_webhook_status(webhook_id, is_enabled=True)
        print("Webhook re-enabled")
        
        # 6. List webhooks by specific IDs
        print("\n=== Listing Specific Webhooks ===")
        specific_webhooks = client.webhooks.list_webhooks(public_ids=[webhook_id])
        print(f"Found {len(specific_webhooks.items)} specific webhooks")
        
        # 7. Work with webhook callbacks
        print("\n=== Working with Webhook Callbacks ===")
        callbacks = client.webhooks.list_callbacks_by_url(
            callback_url=callback_url,
            limit=10,
            offset=0
        )
        print(f"Found {len(callbacks.items)} callbacks for URL {callback_url}")
        
        for callback in callbacks.items:
            print(f"  - Callback ID: {callback.id}, Event: {callback.event}, Status: {callback.status}")
            
            # Get detailed callback information
            callback_detail = client.webhooks.get_callback(callback.id)
            print(f"    Created: {callback_detail.created_at}, Last Call: {callback_detail.last_call_at}")
            
            # If callback failed, you could retry it
            if callback.status == "fail":
                print(f"    Retrying failed callback {callback.id}")
                client.webhooks.retry_callback(callback.id)
        
        # 8. Paginate through all callbacks for a URL
        print("\n=== Paginating Through All Callbacks ===")
        all_callbacks = list(client.webhooks.paginate_callbacks_by_url(
            callback_url=callback_url
        ))
        print(f"Total callbacks found via pagination: {len(all_callbacks)}")
        
        # 9. Get available event types and statuses
        print("\n=== Available Event Types and Statuses ===")
        available_events = client.webhooks.get_available_events()
        print(f"Available event types: {[event.value for event in available_events]}")
        
        available_statuses = client.webhooks.get_available_callback_statuses()
        print(f"Available callback statuses: {[status.value for status in available_statuses]}")
        
        # 10. Delete the webhook (cleanup)
        print("\n=== Cleaning Up - Deleting Webhook ===")
        client.webhooks.delete_webhook(webhook_id)
        print(f"Deleted webhook {webhook_id}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


async def async_webhook_management_example():
    """Example of managing webhooks with the asynchronous client."""
    
    # Initialize the async client
    client = IconicAsyncClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        instance_domain="your-instance.theiconic.com.au"
    )
    
    try:
        # 1. Get available webhook entities and events
        print("=== Getting Available Webhook Entities (Async) ===")
        entities = await client.webhooks.get_entities_async()
        print(f"Found {len(entities.events)} entity types")
        
        # 2. Create a new webhook
        print("\n=== Creating a New Webhook (Async) ===")
        callback_url = "https://your-app.com/webhooks/iconic-async"
        events_to_subscribe = [
            WebhookEventAlias.ORDER_CREATED,
            WebhookEventAlias.PRODUCT_CREATED
        ]
        
        webhook_response = await client.webhooks.create_webhook_async(
            callback_url=callback_url,
            events=events_to_subscribe
        )
        print(f"Created webhook with ID: {webhook_response.webhook_id}")
        
        webhook_id = webhook_response.webhook_id
        
        # 3. List all webhooks
        print("\n=== Listing All Webhooks (Async) ===")
        webhooks_list = await client.webhooks.list_webhooks_async()
        print(f"Found {len(webhooks_list.items)} webhooks")
        
        # 4. Work with webhook callbacks asynchronously
        print("\n=== Working with Webhook Callbacks (Async) ===")
        callbacks = await client.webhooks.list_callbacks_by_url_async(
            callback_url=callback_url,
            limit=5
        )
        print(f"Found {len(callbacks.items)} callbacks for URL {callback_url}")
        
        # 5. Async pagination through callbacks
        print("\n=== Async Pagination Through Callbacks ===")
        callback_count = 0
        async for callback in client.webhooks.paginate_callbacks_by_url_async(
            callback_url=callback_url
        ):
            callback_count += 1
            print(f"  - Callback {callback_count}: {callback.event} ({callback.status})")
            if callback_count >= 10:  # Limit for demo
                break
        
        # 6. Update webhook status
        print("\n=== Managing Webhook Status (Async) ===")
        await client.webhooks.update_webhook_status_async(webhook_id, is_enabled=False)
        print("Webhook disabled")
        
        # 7. Delete the webhook (cleanup)
        print("\n=== Cleaning Up - Deleting Webhook (Async) ===")
        await client.webhooks.delete_webhook_async(webhook_id)
        print(f"Deleted webhook {webhook_id}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()


def webhook_event_handling_example():
    """Example showing how to handle different webhook event types."""
    
    print("=== Webhook Event Handling Example ===")
    
    # Example webhook payloads you might receive
    webhook_payloads = [
        {
            "event": "onOrderCreated",
            "payload": {
                "OrderId": 12345,
                "OrderNr": "ORD-001-123"
            }
        },
        {
            "event": "onProductCreated",
            "payload": {
                "SellerSkus": ["SKU-001", "SKU-002"]
            }
        },
        {
            "event": "onOrderItemsStatusChanged",
            "payload": {
                "OrderId": 12345,
                "OrderItemIds": [1, 2, 3],
                "NewStatus": "ready_to_ship"
            }
        }
    ]
    
    # Process each webhook payload
    for payload in webhook_payloads:
        event_type = payload["event"]
        event_data = payload["payload"]
        
        print(f"\nProcessing event: {event_type}")
        
        if event_type == "onOrderCreated":
            order_id = event_data["OrderId"]
            order_number = event_data["OrderNr"]
            print(f"  New order created: ID={order_id}, Number={order_number}")
            # Here you would typically fetch full order details and process them
            
        elif event_type == "onProductCreated":
            seller_skus = event_data["SellerSkus"]
            print(f"  Products created: {', '.join(seller_skus)}")
            # Here you would typically sync product data or update your catalog
            
        elif event_type == "onOrderItemsStatusChanged":
            order_id = event_data["OrderId"]
            item_ids = event_data["OrderItemIds"]
            new_status = event_data["NewStatus"]
            print(f"  Order {order_id} items {item_ids} changed to status: {new_status}")
            # Here you would typically update order status in your system
            
        else:
            print(f"  Unknown event type: {event_type}")


def webhook_monitoring_example():
    """Example showing how to monitor webhook health and retry failed callbacks."""
    
    client = IconicClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        instance_domain="your-instance.theiconic.com.au"
    )
    
    try:
        print("=== Webhook Monitoring Example ===")
        
        # Monitor all webhooks
        webhooks_list = client.webhooks.list_webhooks()
        
        for webhook in webhooks_list.items:
            print(f"\nMonitoring webhook ID {webhook.id} (URL: {webhook.url})")
            
            # Get recent callbacks for this webhook
            callbacks = client.webhooks.list_callbacks_by_url(
                callback_url=webhook.url,
                limit=50,
                sort="lastCall",
                sort_dir="desc"
            )
            
            # Analyze callback health
            total_callbacks = len(callbacks.items)
            failed_callbacks = [cb for cb in callbacks.items if cb.status == "fail"]
            success_callbacks = [cb for cb in callbacks.items if cb.status == "success"]
            
            success_rate = (len(success_callbacks) / total_callbacks * 100) if total_callbacks > 0 else 0
            
            print(f"  Total callbacks: {total_callbacks}")
            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Failed callbacks: {len(failed_callbacks)}")
            
            # Retry failed callbacks
            if failed_callbacks:
                print(f"  Retrying {len(failed_callbacks)} failed callbacks...")
                for failed_callback in failed_callbacks:
                    try:
                        client.webhooks.retry_callback(failed_callback.id)
                        print(f"    Retried callback {failed_callback.id}")
                    except Exception as e:
                        print(f"    Failed to retry callback {failed_callback.id}: {e}")
    
    except Exception as e:
        print(f"Error during monitoring: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    print("Running Webhook Management Examples\n")
    
    # Run synchronous examples
    print("1. Synchronous Webhook Management:")
    webhook_management_example()
    
    print("\n" + "="*50 + "\n")
    
    # Run asynchronous examples
    print("2. Asynchronous Webhook Management:")
    asyncio.run(async_webhook_management_example())
    
    print("\n" + "="*50 + "\n")
    
    # Show event handling example
    print("3. Webhook Event Handling:")
    webhook_event_handling_example()
    
    print("\n" + "="*50 + "\n")
    
    # Show monitoring example
    print("4. Webhook Monitoring:")
    webhook_monitoring_example()
