import urllib.parse
from typing import Dict, Any, List, Optional, Union, Generator, AsyncGenerator
from datetime import datetime

from .base import IconicResource, T, PaginatedResponse
from ..models.openapi_generated import (
    WebhookEntity,
    WebhookCallback,
    Webhook as WebhookModel
)
from ..models.webhook import (
    WebhookEntitiesResponse,
    CreateWebhookRequest,
    UpdateWebhookRequest,
    WebhookStatusUpdateRequest,
    WebhookResponse,
    WebhookCallback,
    WebhookCallbacksResponse,
    ListWebhooksRequest,
    ListWebhookCallbacksRequest,
    WebhookEventAlias,
    WebhookCallbackStatus,
)


class Webhook(IconicResource):
    """
    Webhook resource representing a single webhook or a collection of webhooks.
    
    When initialized with data, it represents a specific webhook.
    Otherwise, it represents the collection of all webhooks.
    """
    
    endpoint = "webhook"
    model_class = WebhookModel
    
    # Webhook Entities
    
    def get_entities(self) -> WebhookEntitiesResponse:
        """
        Get a list of webhook entities with their available events.
        
        Returns:
            WebhookEntitiesResponse: Object containing all available webhook entities and events
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = "/v2/webhook-entities"
        response = self._client._make_request_sync("GET", url)
        return [WebhookEntity(**item) for item in response['items']]
    
    async def get_entities_async(self) -> WebhookEntitiesResponse:
        """
        Get a list of webhook entities with their available events asynchronously.
        
        Returns:
            WebhookEntitiesResponse: Object containing all available webhook entities and events
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = "/v2/webhook-entities"
        response = await self._client._make_request_async("GET", url)
        return [WebhookEntity(**item) for item in response['items']]
    
    # Webhook Management
    
    def create_webhook(self, callback_url: str, events: List[Union[str, WebhookEventAlias]]) -> WebhookResponse:
        """
        Create a new webhook.
        
        Args:
            callback_url: The URL that will be called by the webhook
            events: List of event aliases to subscribe to
            
        Returns:
            WebhookResponse: Response containing webhook ID and creation timestamp
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Convert enum values to strings if needed
        event_strings = [event.value if isinstance(event, WebhookEventAlias) else event for event in events]
        
        request_data = CreateWebhookRequest(
            callbackUrl=callback_url,
            events=event_strings
        )
        
        url = "/v2/webhook"
        prepared_data = self._prepare_request_data(request_data.model_dump(by_alias=True))
        response = self._client._make_request_sync("POST", url, json_data=prepared_data)
        
        return WebhookResponse(**response)
    
    async def create_webhook_async(self, callback_url: str, events: List[Union[str, WebhookEventAlias]]) -> WebhookResponse:
        """
        Create a new webhook asynchronously.
        
        Args:
            callback_url: The URL that will be called by the webhook
            events: List of event aliases to subscribe to
            
        Returns:
            WebhookResponse: Response containing webhook ID and creation timestamp
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Convert enum values to strings if needed
        event_strings = [event.value if isinstance(event, WebhookEventAlias) else event for event in events]
        
        request_data = CreateWebhookRequest(
            callbackUrl=callback_url,
            events=event_strings
        )
        
        url = "/v2/webhook"
        prepared_data = self._prepare_request_data(request_data.model_dump(by_alias=True))
        response = await self._client._make_request_async("POST", url, json_data=prepared_data)
        
        return WebhookResponse(**response)
    
    def update_webhook(self, webhook_uuid: str, callback_url: str, events: List[Union[str, WebhookEventAlias]]) -> WebhookResponse:
        """
        Update an existing webhook.
        
        Args:
            webhook_uuid: UUID of the webhook to update
            callback_url: The new URL that will be called by the webhook
            events: List of event aliases to subscribe to
            
        Returns:
            WebhookResponse: Response containing webhook ID and update timestamp
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Convert enum values to strings if needed
        event_strings = [event.value if isinstance(event, WebhookEventAlias) else event for event in events]
        
        request_data = UpdateWebhookRequest(
            callback_url=callback_url,
            events=event_strings
        )
        
        url = f"/v2/webhook/{webhook_uuid}"
        prepared_data = self._prepare_request_data(request_data.model_dump(by_alias=True))
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return WebhookResponse(**response)
    
    async def update_webhook_async(self, webhook_uuid: str, callback_url: str, events: List[Union[str, WebhookEventAlias]]) -> WebhookResponse:
        """
        Update an existing webhook asynchronously.
        
        Args:
            webhook_uuid: UUID of the webhook to update
            callback_url: The new URL that will be called by the webhook
            events: List of event aliases to subscribe to
            
        Returns:
            WebhookResponse: Response containing webhook ID and update timestamp
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Convert enum values to strings if needed
        event_strings = [event.value if isinstance(event, WebhookEventAlias) else event for event in events]
        
        request_data = UpdateWebhookRequest(
            callback_url=callback_url,
            events=event_strings
        )
        
        url = f"/v2/webhook/{webhook_uuid}"
        prepared_data = self._prepare_request_data(request_data.model_dump(by_alias=True))
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return WebhookResponse(**response)
    
    def delete_webhook(self, webhook_uuid: str) -> None:
        """
        Delete a webhook.
        
        Args:
            webhook_uuid: UUID of the webhook to delete
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/v2/webhook/{webhook_uuid}"
        self._client._make_request_sync("DELETE", url)
    
    async def delete_webhook_async(self, webhook_uuid: str) -> None:
        """
        Delete a webhook asynchronously.
        
        Args:
            webhook_uuid: UUID of the webhook to delete
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/v2/webhook/{webhook_uuid}"
        await self._client._make_request_async("DELETE", url)
    
    def update_webhook_status(self, webhook_uuid: str, is_enabled: bool) -> None:
        """
        Update the enabled/disabled status of a webhook.
        
        Args:
            webhook_uuid: UUID of the webhook to update
            is_enabled: Whether the webhook should be enabled or disabled
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        request_data = WebhookStatusUpdateRequest(is_enabled=is_enabled)
        
        url = f"/v2/webhook/{webhook_uuid}/status"
        prepared_data = self._prepare_request_data(request_data.model_dump(by_alias=True))
        self._client._make_request_sync("POST", url, json_data=prepared_data)
    
    async def update_webhook_status_async(self, webhook_uuid: str, is_enabled: bool) -> None:
        """
        Update the enabled/disabled status of a webhook asynchronously.
        
        Args:
            webhook_uuid: UUID of the webhook to update
            is_enabled: Whether the webhook should be enabled or disabled
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        request_data = WebhookStatusUpdateRequest(is_enabled=is_enabled)
        
        url = f"/v2/webhook/{webhook_uuid}/status"
        prepared_data = self._prepare_request_data(request_data.model_dump(by_alias=True))
        await self._client._make_request_async("POST", url, json_data=prepared_data)
    
    # Webhook Listing
    
    def list_webhooks(self, public_ids: Optional[List[str]] = None) -> List["Webhook"]:
        """
        Get a list of webhooks.
        
        Args:
            public_ids: Optional list of webhook IDs to filter by
            
        Returns:
            List[Webhook]: List of webhook objects
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = "/v2/webhooks"
        params = {}
        
        if public_ids:
            params["publicIds[]"] = public_ids
        
        response = self._client._make_request_sync("GET", url, params=params)
        return [Webhook(client=self._client, data=item) for item in response['items']]
    
    async def list_webhooks_async(self, public_ids: Optional[List[str]] = None) -> List["Webhook"]:
        """
        Get a list of webhooks asynchronously.
        
        Args:
            public_ids: Optional list of webhook IDs to filter by
            
        Returns:
            List[Webhook]: List of webhook objects
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = "/v2/webhooks"
        params = {}
        
        if public_ids:
            params["publicIds[]"] = public_ids
        
        response = await self._client._make_request_async("GET", url, params=params)
        return [Webhook(client=self._client, data=item) for item in response['items']]
    
    # Webhook Callbacks
    
    def get_callback(self, callback_id: int) -> WebhookCallback:
        """
        Get a webhook callback detail by ID.
        
        Args:
            callback_id: Numeric ID of the webhook callback
            
        Returns:
            WebhookCallback: The webhook callback details
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/v2/webhook/callback/{callback_id}"
        response = self._client._make_request_sync("GET", url)
        return WebhookCallback(**response)
    
    async def get_callback_async(self, callback_id: int) -> WebhookCallback:
        """
        Get a webhook callback detail by ID asynchronously.
        
        Args:
            callback_id: Numeric ID of the webhook callback
            
        Returns:
            WebhookCallback: The webhook callback details
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/v2/webhook/callback/{callback_id}"
        response = await self._client._make_request_async("GET", url)
        return WebhookCallback(**response)
    
    def retry_callback(self, callback_id: int) -> None:
        """
        Retry a webhook callback.
        
        Args:
            callback_id: Numeric ID of the webhook callback to retry
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/v2/webhook/callback/{callback_id}/retry/"
        self._client._make_request_sync("POST", url)
    
    async def retry_callback_async(self, callback_id: int) -> None:
        """
        Retry a webhook callback asynchronously.
        
        Args:
            callback_id: Numeric ID of the webhook callback to retry
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/v2/webhook/callback/{callback_id}/retry/"
        await self._client._make_request_async("POST", url)
    
    def list_callbacks_by_url(
        self,
        callback_url: str,
        limit: int = 100,
        offset: int = 0,
        sort_dir: Optional[str] = "asc",
        sort: Optional[str] = None
    ) -> WebhookCallbacksResponse:
        """
        Get a list of webhook callbacks by callback URL.
        
        Args:
            callback_url: The webhook callback URL (will be URL encoded)
            limit: Maximum number of items to return
            offset: Starting point in the collection
            sort_dir: Sort direction ('asc' or 'desc')
            sort: Sort field ('callbackUrl' or 'lastCall')
            
        Returns:
            WebhookCallbacksResponse: Response containing webhook callbacks and pagination info
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # URL encode the callback URL
        encoded_callback_url = urllib.parse.quote(callback_url, safe='')
        url = f"/v2/webhook/callbacks/{encoded_callback_url}"
        
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if sort_dir:
            params["sortDir"] = sort_dir
        if sort:
            params["sort"] = sort
        
        response = self._client._make_request_sync("GET", url, params=params)
        return WebhookCallbacksResponse(**response)
    
    async def list_callbacks_by_url_async(
        self,
        callback_url: str,
        limit: int = 100,
        offset: int = 0,
        sort_dir: Optional[str] = "asc",
        sort: Optional[str] = None
    ) -> WebhookCallbacksResponse:
        """
        Get a list of webhook callbacks by callback URL asynchronously.
        
        Args:
            callback_url: The webhook callback URL (will be URL encoded)
            limit: Maximum number of items to return
            offset: Starting point in the collection
            sort_dir: Sort direction ('asc' or 'desc')
            sort: Sort field ('callbackUrl' or 'lastCall')
            
        Returns:
            WebhookCallbacksResponse: Response containing webhook callbacks and pagination info
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # URL encode the callback URL
        encoded_callback_url = urllib.parse.quote(callback_url, safe='')
        url = f"/v2/webhook/callbacks/{encoded_callback_url}"
        
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if sort_dir:
            params["sortDir"] = sort_dir
        if sort:
            params["sort"] = sort
        
        response = await self._client._make_request_async("GET", url, params=params)
        return WebhookCallbacksResponse(**response)
    
    # Convenience methods for pagination
    
    def paginate_callbacks_by_url(
        self,
        callback_url: str,
        sort_dir: Optional[str] = "asc",
        sort: Optional[str] = None,
        **params
    ) -> Generator[WebhookCallback, None, None]:
        """
        Generator that yields all webhook callbacks for a given URL.
        
        Args:
            callback_url: The webhook callback URL
            sort_dir: Sort direction ('asc' or 'desc')
            sort: Sort field ('callbackUrl' or 'lastCall')
            **params: Additional pagination parameters
            
        Yields:
            WebhookCallback instances one at a time
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        
        while True:
            response = self.list_callbacks_by_url(
                callback_url=callback_url,
                limit=limit,
                offset=offset,
                sort_dir=sort_dir,
                sort=sort
            )
            
            if not response.items:
                break
                
            for callback in response.items:
                yield callback
                
            if len(response.items) < limit:
                break
                
            offset += limit
    
    async def paginate_callbacks_by_url_async(
        self,
        callback_url: str,
        sort_dir: Optional[str] = "asc",
        sort: Optional[str] = None,
        **params
    ) -> AsyncGenerator[WebhookCallback, None]:
        """
        Async generator that yields all webhook callbacks for a given URL.
        
        Args:
            callback_url: The webhook callback URL
            sort_dir: Sort direction ('asc' or 'desc')
            sort: Sort field ('callbackUrl' or 'lastCall')
            **params: Additional pagination parameters
            
        Yields:
            WebhookCallback instances one at a time
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        
        while True:
            response = await self.list_callbacks_by_url_async(
                callback_url=callback_url,
                limit=limit,
                offset=offset,
                sort_dir=sort_dir,
                sort=sort
            )
            
            if not response.items:
                break
                
            for callback in response.items:
                yield callback
                
            if len(response.items) < limit:
                break
                
            offset += limit
    
    # Utility methods
    
    @staticmethod
    def get_available_events() -> List[WebhookEventAlias]:
        """
        Get a list of all available webhook event aliases.
        
        Returns:
            List of WebhookEventAlias enum values
        """
        return list(WebhookEventAlias)
    
    @staticmethod
    def get_available_callback_statuses() -> List[WebhookCallbackStatus]:
        """
        Get a list of all available webhook callback statuses.
        
        Returns:
            List of WebhookCallbackStatus enum values
        """
        return list(WebhookCallbackStatus)


# Alias for backwards compatibility
WebhookResource = Webhook
