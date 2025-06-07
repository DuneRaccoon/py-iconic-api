from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum

from .openapi_generated import (
    WebhookCallback
)


class WebhookEventAlias(str, Enum):
    """Available webhook event aliases."""
    FEED_COMPLETED = "onFeedCompleted"
    FEED_CREATED = "onFeedCreated"
    ORDER_CREATED = "onOrderCreated"
    ORDER_ITEMS_STATUS_CHANGED = "onOrderItemsStatusChanged"
    PRODUCT_CREATED = "onProductCreated"
    PRODUCT_QC_STATUS_CHANGED = "onProductQcStatusChanged"
    PRODUCT_UPDATED = "onProductUpdated"
    RETURN_STATUS_CHANGED = "onReturnStatusChanged"
    STATISTICS_UPDATED = "onStatisticsUpdated"


class WebhookCallbackStatus(str, Enum):
    """Webhook callback status options."""
    SUCCESS = "success"
    FAIL = "fail"
    IN_PROGRESS = "inprogress"
    QUEUEING_FAILED = "queueing_failed"


class WebhookEntity(BaseModel):
    """Webhook entity model."""
    name: str = Field(..., description="Human readable string identifier of an Entity")
    events: List["WebhookEvent"] = Field(..., description="List of events for this entity")


class WebhookEvent(BaseModel):
    """Webhook event model."""
    name: str = Field(..., description="Human readable string identifier of an Event")
    alias: str = Field(..., description="Human readable string identifier of an Event combined with its Entity")


class WebhookEntitiesResponse(BaseModel):
    """Response model for webhook entities."""
    events: List[WebhookEntity] = Field(..., description="List of webhook entities")


class CreateWebhookRequest(BaseModel):
    """Request model for creating a webhook."""
    callback_url: str = Field(..., alias="callbackUrl", description="The webhook url that will be called by SellerCenter")
    events: List[str] = Field(..., description="List of webhook related events identified by its alias")


class UpdateWebhookRequest(BaseModel):
    """Request model for updating a webhook."""
    callback_url: str = Field(..., alias="callbackUrl", description="The webhook url that will be called by SellerCenter")
    events: List[str] = Field(..., description="List of webhook related events identified by its alias")


class WebhookStatusUpdateRequest(BaseModel):
    """Request model for updating webhook status."""
    is_enabled: bool = Field(..., alias="isEnabled", description="The status of the webhook")


class WebhookResponse(BaseModel):
    """Response model for webhook creation/update."""
    webhook_id: str = Field(..., alias="webhookId", description="Webhook identifier")
    created_at: Optional[datetime] = Field(None, alias="createdAt", description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt", description="Update timestamp")

class PaginationInfo(BaseModel):
    """Pagination information model."""
    limit: int = Field(..., description="Entity limit per request")
    offset: int = Field(..., description="Offset for entities in repository")
    total_count: int = Field(..., alias="totalCount", description="Total count of entities for request")


class WebhookCallbacksResponse(BaseModel):
    """Response model for webhook callbacks listing."""
    items: List[WebhookCallback] = Field(..., description="List of webhook callbacks")
    pagination: PaginationInfo = Field(..., description="Pagination information")


class ListWebhooksRequest(BaseModel):
    """Request model for listing webhooks."""
    public_ids: Optional[List[str]] = Field(None, alias="publicIds[]", description="Search by webhook ids")


class ListWebhookCallbacksRequest(BaseModel):
    """Request model for listing webhook callbacks by URL."""
    callback_url: str = Field(..., description="The Webhook callback url (encoded)")
    sort_dir: Optional[Literal["asc", "desc"]] = Field("asc", alias="sortDir", description="Sort direction")
    sort: Optional[Literal["callbackUrl", "lastCall"]] = Field(None, description="Sort field")
    limit: int = Field(..., description="Maximum number of items to return")
    offset: int = Field(..., description="Starting point in collection")


# Feed payload models
class FeedPayload(BaseModel):
    """Feed event payload model."""
    feed: str = Field(..., alias="Feed", description="A feed identifier to be used to get more details using the API")


class FeedCreatedEvent(BaseModel):
    """Feed created event model."""
    event: Literal["onFeedCreated"] = Field(..., description="Event type")
    payload: FeedPayload = Field(..., description="Event payload")


class FeedCompletedEvent(BaseModel):
    """Feed completed event model."""
    event: Literal["onFeedCompleted"] = Field(..., description="Event type")
    payload: FeedPayload = Field(..., description="Event payload")


# Product payload models
class ProductPayload(BaseModel):
    """Product event payload model."""
    seller_skus: List[str] = Field(..., alias="SellerSkus", description="List of seller skus to be used to get more details using the API")


class ProductCreatedEvent(BaseModel):
    """Product created event model."""
    event: Literal["onProductCreated"] = Field(..., description="Event type")
    payload: ProductPayload = Field(..., description="Event payload")


class ProductUpdatedEvent(BaseModel):
    """Product updated event model."""
    event: Literal["onProductUpdated"] = Field(..., description="Event type")
    payload: ProductPayload = Field(..., description="Event payload")


class ProductQcStatusChangedEvent(BaseModel):
    """Product QC status changed event model."""
    event: Literal["onProductQcStatusChanged"] = Field(..., description="Event type")
    payload: ProductPayload = Field(..., description="Event payload")


# Order payload models
class OrderCreatedPayload(BaseModel):
    """Order created event payload model."""
    order_id: int = Field(..., alias="OrderId", description="Order identifier to be used to get more details using the API")
    order_nr: str = Field(..., alias="OrderNr", description="Order number")


class OrderCreatedEvent(BaseModel):
    """Order created event model."""
    event: Literal["onOrderCreated"] = Field(..., description="Event type")
    payload: OrderCreatedPayload = Field(..., description="Event payload")


class OrderItemsStatusChangedPayload(BaseModel):
    """Order items status changed event payload model."""
    order_id: int = Field(..., alias="OrderId", description="Order identifier to be used to get more details using the API")
    order_item_ids: List[int] = Field(..., alias="OrderItemIds", description="Order Item identifiers to be used to get more details using the API")
    new_status: str = Field(..., alias="NewStatus", description="New item status")


class OrderItemsStatusChangedEvent(BaseModel):
    """Order items status changed event model."""
    event: Literal["onOrderItemsStatusChanged"] = Field(..., description="Event type")
    payload: OrderItemsStatusChangedPayload = Field(..., description="Event payload")


# Statistics payload models
class StatisticsUpdatedEvent(BaseModel):
    """Statistics updated event model."""
    event: Literal["onStatisticsUpdated"] = Field(..., description="Event type")
    payload: Dict[str, Any] = Field(..., description="Event payload (empty object)")


# Union type for all webhook events
WebhookEventPayload = Union[
    FeedCreatedEvent,
    FeedCompletedEvent,
    ProductCreatedEvent,
    ProductUpdatedEvent,
    ProductQcStatusChangedEvent,
    OrderCreatedEvent,
    OrderItemsStatusChangedEvent,
    StatisticsUpdatedEvent,
]


# Update forward references
WebhookEntity.model_rebuild()
