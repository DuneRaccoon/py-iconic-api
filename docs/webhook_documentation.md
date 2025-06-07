# Webhook Resource Documentation

This document describes the webhook resource implementation for the Iconic API client package.

## Overview

The webhook resource provides complete functionality for managing webhooks within the Iconic Seller Center API. It supports all webhook-related operations including creation, updating, deletion, status management, and callback monitoring.

## Features

### Core Webhook Management
- **Create webhooks** - Subscribe to specific events with custom callback URLs
- **Update webhooks** - Modify existing webhook configurations
- **Delete webhooks** - Remove webhooks when no longer needed
- **Status management** - Enable/disable webhooks as needed

### Webhook Monitoring
- **List webhooks** - Get all webhooks or filter by specific IDs
- **Callback management** - View, retry, and monitor webhook callbacks
- **Pagination support** - Handle large numbers of callbacks efficiently

### Event Types
The following webhook events are supported:
- `onFeedCompleted` - Feed processing completed
- `onFeedCreated` - New feed created
- `onOrderCreated` - New order created
- `onOrderItemsStatusChanged` - Order item status changed
- `onProductCreated` - New product created
- `onProductQcStatusChanged` - Product QC status changed
- `onProductUpdated` - Product updated
- `onReturnStatusChanged` - Return status changed
- `onStatisticsUpdated` - Statistics updated

## Usage Examples

### Basic Webhook Creation

```python
from iconic_api import IconicClient
from iconic_api.models.webhook import WebhookEventAlias

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your-instance.theiconic.com.au"
)

# Create a webhook
webhook = client.webhooks.create_webhook(
    callback_url="https://your-app.com/webhooks/iconic",
    events=[
        WebhookEventAlias.ORDER_CREATED,
        WebhookEventAlias.PRODUCT_CREATED
    ]
)

print(f"Created webhook: {webhook.webhook_id}")
```

### Webhook Management

```python
# List all webhooks
webhooks = client.webhooks.list_webhooks()
for webhook in webhooks.items:
    print(f"Webhook {webhook.id}: {webhook.url}")

# Update webhook
updated_webhook = client.webhooks.update_webhook(
    webhook_uuid="your-webhook-uuid",
    callback_url="https://your-app.com/new-webhook-url",
    events=[WebhookEventAlias.ORDER_CREATED]
)

# Disable webhook
client.webhooks.update_webhook_status("your-webhook-uuid", is_enabled=False)

# Delete webhook
client.webhooks.delete_webhook("your-webhook-uuid")
```

### Callback Monitoring

```python
# Get callbacks for a specific URL
callbacks = client.webhooks.list_callbacks_by_url(
    callback_url="https://your-app.com/webhooks/iconic",
    limit=50
)

# Check callback health
for callback in callbacks.items:
    if callback.status == "fail":
        print(f"Failed callback {callback.id}: {callback.event}")
        # Retry failed callback
        client.webhooks.retry_callback(callback.id)

# Paginate through all callbacks
for callback in client.webhooks.paginate_callbacks_by_url(
    callback_url="https://your-app.com/webhooks/iconic"
):
    print(f"Callback: {callback.event} - {callback.status}")
```

### Asynchronous Usage

```python
import asyncio
from iconic_api import IconicAsyncClient

async def manage_webhooks():
    client = IconicAsyncClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        instance_domain="your-instance.theiconic.com.au"
    )
    
    # All methods have async equivalents
    webhook = await client.webhooks.create_webhook_async(
        callback_url="https://your-app.com/webhooks/iconic",
        events=[WebhookEventAlias.ORDER_CREATED]
    )
    
    # Async pagination
    async for callback in client.webhooks.paginate_callbacks_by_url_async(
        callback_url="https://your-app.com/webhooks/iconic"
    ):
        print(f"Async callback: {callback.event}")
    
    await client.close()

asyncio.run(manage_webhooks())
```

## Webhook Event Payloads

### Order Created
```json
{
    "event": "onOrderCreated",
    "payload": {
        "OrderId": 190,
        "OrderNr": "123221"
    }
}
```

### Product Created
```json
{
    "event": "onProductCreated",
    "payload": {
        "SellerSkus": ["NI006ELAAGWDNAFAMZ-43340"]
    }
}
```

### Order Items Status Changed
```json
{
    "event": "onOrderItemsStatusChanged",
    "payload": {
        "OrderId": 190,
        "OrderItemIds": [2, 3],
        "NewStatus": "ready_to_ship"
    }
}
```

## Error Handling

The webhook resource follows the same error handling patterns as other resources in the package:

```python
from iconic_api.exceptions import IconicAPIError, AuthenticationError

try:
    webhook = client.webhooks.create_webhook(
        callback_url="https://invalid-url",
        events=["invalid_event"]
    )
except IconicAPIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
```

## Retry Logic

The webhook system includes automatic retry logic for failed callbacks:

- **Retry Schedule**: Callbacks are retried with exponential backoff
- **Maximum Retries**: Up to 16 retries over 30 days
- **Manual Retry**: Failed callbacks can be manually retried using `retry_callback()`

## Rate Limiting

Webhook operations are subject to the same rate limiting as other API operations:
- Default: 25 requests per second
- Configurable via client initialization
- Automatic retry with backoff on rate limit hits

## Models

The webhook resource uses strongly-typed Pydantic models for all data structures:

- `WebhookEventAlias` - Enum of available event types
- `WebhookCallbackStatus` - Enum of callback statuses
- `CreateWebhookRequest` - Request model for creating webhooks
- `UpdateWebhookRequest` - Request model for updating webhooks
- `WebhookResponse` - Response model for webhook operations
- `WebhookCallback` - Model representing a webhook callback
- `WebhookEntitiesResponse` - Response model for available entities

## Integration with Existing Resources

The webhook resource integrates seamlessly with existing resources:

```python
# Access via client
client.webhooks.create_webhook(...)

# Same patterns as other resources
webhooks = client.webhooks.list(paginated=True)
webhook = client.webhooks.get("webhook-id")
```

## Testing

A comprehensive test suite is provided in `test_webhook_integration.py` and examples in `examples/webhook_management_example.py`.

## File Structure

```
iconic_api/
├── models/
│   └── webhook.py              # Pydantic models and enums
├── resources/
│   └── webhook.py              # Webhook resource implementation
├── client.py                   # Updated to include webhook resource
examples/
└── webhook_management_example.py   # Comprehensive usage examples
test_webhook_integration.py         # Integration tests
```

This implementation provides a complete, production-ready webhook management system that follows the existing patterns and conventions of the Iconic API client package.
