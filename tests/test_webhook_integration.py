#!/usr/bin/env python3
"""
Simple test to verify webhook resource integration.
This test doesn't make actual API calls but verifies the resource is properly integrated.
"""

from iconic_api import IconicClient, IconicAsyncClient
from iconic_api.models.webhook import WebhookEventAlias, WebhookCallbackStatus
from iconic_api.resources.webhook import Webhook


def test_webhook_integration():
    """Test that webhook resource is properly integrated into the client."""
    
    # Test synchronous client
    client = IconicClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        instance_domain="test-instance.theiconic.com.au"
    )
    
    print("=== Testing Webhook Resource Integration ===")
    
    # Verify webhook resource exists
    assert hasattr(client, 'webhooks'), "Client should have webhooks attribute"
    assert isinstance(client.webhooks, Webhook), "webhooks should be a Webhook instance"
    
    print("✓ Webhook resource properly attached to synchronous client")
    
    # Test asynchronous client
    async_client = IconicAsyncClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        instance_domain="test-instance.theiconic.com.au"
    )
    
    assert hasattr(async_client, 'webhooks'), "Async client should have webhooks attribute"
    assert isinstance(async_client.webhooks, Webhook), "webhooks should be a Webhook instance"
    
    print("✓ Webhook resource properly attached to asynchronous client")
    
    # Test enum availability
    events = list(WebhookEventAlias)
    assert len(events) > 0, "Should have webhook event aliases"
    print(f"✓ Found {len(events)} webhook event aliases")
    
    statuses = list(WebhookCallbackStatus)
    assert len(statuses) > 0, "Should have webhook callback statuses"
    print(f"✓ Found {len(statuses)} webhook callback statuses")
    
    # Test utility methods
    available_events = Webhook.get_available_events()
    assert len(available_events) > 0, "Should return available events"
    print(f"✓ get_available_events() returns {len(available_events)} events")
    
    available_statuses = Webhook.get_available_callback_statuses()
    assert len(available_statuses) > 0, "Should return available statuses"
    print(f"✓ get_available_callback_statuses() returns {len(available_statuses)} statuses")
    
    # Test method existence (without calling them)
    webhook_methods = [
        'get_entities', 'get_entities_async',
        'create_webhook', 'create_webhook_async',
        'update_webhook', 'update_webhook_async',
        'delete_webhook', 'delete_webhook_async',
        'update_webhook_status', 'update_webhook_status_async',
        'list_webhooks', 'list_webhooks_async',
        'get_callback', 'get_callback_async',
        'retry_callback', 'retry_callback_async',
        'list_callbacks_by_url', 'list_callbacks_by_url_async',
        'paginate_callbacks_by_url', 'paginate_callbacks_by_url_async'
    ]
    
    for method_name in webhook_methods:
        assert hasattr(client.webhooks, method_name), f"Should have method {method_name}"
    
    print(f"✓ All {len(webhook_methods)} webhook methods are available")
    
    # Clean up
    client.close()
    
    print("\n✅ All webhook integration tests passed!")


def test_webhook_models():
    """Test that webhook models can be instantiated and work correctly."""
    
    print("\n=== Testing Webhook Models ===")
    
    from iconic_api.models.webhook import (
        CreateWebhookRequest,
        UpdateWebhookRequest,
        WebhookStatusUpdateRequest,
        WebhookResponse,
        WebhookCallback,
        WebhookEntitiesResponse,
        WebhookEntity,
        WebhookEvent
    )
    
    # Test CreateWebhookRequest
    create_request = CreateWebhookRequest(
        callback_url="https://example.com/webhook",
        events=["onOrderCreated", "onProductCreated"]
    )
    assert create_request.callback_url == "https://example.com/webhook"
    assert len(create_request.events) == 2
    print("✓ CreateWebhookRequest model works correctly")
    
    # Test model serialization with aliases
    create_data = create_request.model_dump(by_alias=True)
    assert "callbackUrl" in create_data
    assert create_data["callbackUrl"] == "https://example.com/webhook"
    print("✓ Model serialization with aliases works correctly")
    
    # Test UpdateWebhookRequest
    update_request = UpdateWebhookRequest(
        callback_url="https://example.com/updated-webhook",
        events=["onOrderCreated"]
    )
    assert update_request.callback_url == "https://example.com/updated-webhook"
    print("✓ UpdateWebhookRequest model works correctly")
    
    # Test WebhookStatusUpdateRequest
    status_request = WebhookStatusUpdateRequest(is_enabled=True)
    assert status_request.is_enabled == True
    
    status_data = status_request.model_dump(by_alias=True)
    assert "isEnabled" in status_data
    print("✓ WebhookStatusUpdateRequest model works correctly")
    
    # Test WebhookEvent
    event = WebhookEvent(name="Created", alias="onOrderCreated")
    assert event.name == "Created"
    assert event.alias == "onOrderCreated"
    print("✓ WebhookEvent model works correctly")
    
    # Test WebhookEntity
    entity = WebhookEntity(name="Order", events=[event])
    assert entity.name == "Order"
    assert len(entity.events) == 1
    print("✓ WebhookEntity model works correctly")
    
    print("\n✅ All webhook model tests passed!")


def test_webhook_enums():
    """Test webhook enums and their values."""
    
    print("\n=== Testing Webhook Enums ===")
    
    # Test WebhookEventAlias enum
    assert WebhookEventAlias.ORDER_CREATED.value == "onOrderCreated"
    assert WebhookEventAlias.PRODUCT_CREATED.value == "onProductCreated"
    assert WebhookEventAlias.FEED_COMPLETED.value == "onFeedCompleted"
    print("✓ WebhookEventAlias enum values are correct")
    
    # Test WebhookCallbackStatus enum
    assert WebhookCallbackStatus.SUCCESS.value == "success"
    assert WebhookCallbackStatus.FAIL.value == "fail"
    assert WebhookCallbackStatus.IN_PROGRESS.value == "inprogress"
    print("✓ WebhookCallbackStatus enum values are correct")
    
    # Test enum iteration
    all_events = list(WebhookEventAlias)
    expected_events = [
        "onFeedCompleted", "onFeedCreated", "onOrderCreated",
        "onOrderItemsStatusChanged", "onProductCreated",
        "onProductQcStatusChanged", "onProductUpdated",
        "onReturnStatusChanged", "onStatisticsUpdated"
    ]
    
    event_values = [event.value for event in all_events]
    for expected_event in expected_events:
        assert expected_event in event_values, f"Expected event {expected_event} not found"
    
    print(f"✓ All {len(expected_events)} expected webhook events are available")
    
    print("\n✅ All webhook enum tests passed!")


if __name__ == "__main__":
    print("Running Webhook Resource Integration Tests\n")
    
    try:
        test_webhook_integration()
        test_webhook_models()
        test_webhook_enums()
        
        print("\n🎉 All tests passed! Webhook resource is properly integrated.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
