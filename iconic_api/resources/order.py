from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple, Union, Generator, Literal
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

from .base import IconicResource, T
from .finance import Finance
from .order_item import DeliveryType, OrderItemResource
from .transaction import Transaction
from .. import utils
from ..models import (
    Order as OrderModel,
    OrderFinance,
    OrderHistory,
    OrderItem,
    ListOrdersRequest
)

class BulkFetchTransactionsData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    order: "Order"
    transactions: List["Transaction"]
    
    def get_transactions_for_order_item(self, order_item: OrderItem, groupName: Optional[str] = None) -> Optional[List["Transaction"]]:
        """Helper to get the transactions for a specific order item.

        If groupName is provided, it will filter transactions by that group name. (e.g. 'Revenue AU (incl. GST)')
        """
        transactions = [
            transaction for transaction in self.transactions
            if transaction.orderItemId == order_item.id
        ]
        if groupName:
            transactions = [
                transaction for transaction in transactions
                if transaction.groupName == groupName
            ]
        return transactions if transactions else None
        
    
class Order(IconicResource):
    """
    Order resource representing a single order or a collection of orders.
    
    When initialized with data, it represents a specific order.
    Otherwise, it represents the collection of all orders.
    """
    
    endpoint = "orders"
    model_class = OrderModel

    #: Target status (and the aliases callers already use) -> the
    #: ``OrderItemResource`` method that performs it. The API has no order level
    #: status endpoint, so every one of these fans out over the order's items.
    _STATUS_TRANSITIONS = {
        "ready_to_ship": "set_to_ready_to_ship",
        "packed": "set_to_packed_by_marketplace",
        "packed_by_marketplace": "set_to_packed_by_marketplace",
        "shipped": "set_to_shipped",
        "delivered": "set_to_delivered",
        "canceled": "set_to_cancelled",
        "cancelled": "set_to_cancelled",
        "failed": "set_to_delivery_failed",
        "delivery_failed": "set_to_delivery_failed",
        "returned": "set_to_returned",
        "return_approved": "set_to_return_approved",
        "return_received": "set_to_return_received",
        "return_rejected": "set_to_return_rejected",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self._data:
            self._model: OrderModel = self.model_class(**self._data)
        else:
            self._model = None
    
    def paginate(self: T, **params: ListOrdersRequest) -> Generator["Order", None, None]:
        """Generator to paginate through orders."""
        if not isinstance(params, ListOrdersRequest):
            params = ListOrdersRequest(**params)
            
        params = params.to_api_params()
        
        return super().paginate(**params)
    
    def list_orders(self, **params: Union[Dict[str, Any], ListOrdersRequest]) -> List["Order"]:
        """List orders based on filter criteria."""
        if not isinstance(params, ListOrdersRequest):
            params = ListOrdersRequest(**params)
            
        params = params.to_api_params()
            
        url = "/v2/orders"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            if isinstance(response, dict) and "items" in response:
                items = response.get("items", [])
            else:
                items = response
            return [Order(client=self._client, data=item) for item in items]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_orders_async(self, **params: Union[Dict[str, Any], ListOrdersRequest]) -> List["Order"]:
        """List orders based on filter criteria asynchronously."""
        if not isinstance(params, ListOrdersRequest):
            params = ListOrdersRequest(**params)
            
        params = params.to_api_params()
        
        url = "/v2/orders"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            if isinstance(response, dict) and "items" in response:
                items = response.get("items", [])
            else:
                items = response
            return [Order(client=self._client, data=item) for item in items]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_by_order_id(self, order_id: Union[int, str]) -> "Order":
        """
        Get an order by its numeric Iconic order id.

        The path parameter of GET /v2/orders/{orderId} is the *numeric* order id
        (``Order.id``), not the seller's order number (``Order.number``).
        Passing an order number here returns a 404.

        Args:
            order_id: Numeric order id

        Returns:
            The order
        """
        url = f"/v2/orders/{order_id}"

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return Order(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_by_order_id_async(self, order_id: Union[int, str]) -> "Order":
        """
        Get an order by its numeric Iconic order id, asynchronously.

        Args:
            order_id: Numeric order id

        Returns:
            The order
        """
        url = f"/v2/orders/{order_id}"

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return Order(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def get_by_order_number(self, order_number: Union[int, str]) -> "Order":
        """
        Deprecated alias of :meth:`get_by_order_id`.

        Despite the name this has always issued GET /v2/orders/{orderId}, whose
        path parameter is the numeric order id -- there is no lookup by order
        number in the API. Kept so existing callers keep working; new code
        should call ``get_by_order_id`` and pass ``Order.id``.

        Args:
            order_number: Numeric order id, despite the parameter name

        Returns:
            The order
        """
        return self.get_by_order_id(order_number)

    async def get_by_order_number_async(self, order_number: Union[int, str]) -> "Order":
        """
        Deprecated alias of :meth:`get_by_order_id_async`.

        Args:
            order_number: Numeric order id, despite the parameter name

        Returns:
            The order
        """
        return await self.get_by_order_id_async(order_number)

    def get_documents(self) -> List[Dict[str, Any]]:
        """Get documents for this order."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot get documents without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/documents"
        
        if hasattr(self._client, '_make_request_sync'):
            return self._client._make_request_sync("GET", url)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_documents_async(self) -> List[Dict[str, Any]]:
        """Get documents for this order asynchronously."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot get documents without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/documents"
        
        if hasattr(self._client, '_make_request_async'):
            return await self._client._make_request_async("GET", url)
        else:
            raise TypeError("This method requires an asynchronous client")

    def get_history(self, order_item_ids: Optional[List[int]] = None) -> List[OrderHistory]:
        """
        Get the status change history of every order item of this order.

        Args:
            order_item_ids: Restrict the history to these order items

        Returns:
            One entry per recorded status change, oldest first
        """
        if not self.id:
            raise ValueError("Cannot get the history without an order id")

        url = f"/v2/order/{self.id}/history"
        params: Dict[str, Any] = {}

        if order_item_ids:
            params["order_item_ids"] = [int(item_id) for item_id in order_item_ids]

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [OrderHistory(**item) for item in (response or [])]
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_history_async(self, order_item_ids: Optional[List[int]] = None) -> List[OrderHistory]:
        """
        Get the status change history of every order item of this order, asynchronously.

        Args:
            order_item_ids: Restrict the history to these order items

        Returns:
            One entry per recorded status change, oldest first
        """
        if not self.id:
            raise ValueError("Cannot get the history without an order id")

        url = f"/v2/order/{self.id}/history"
        params: Dict[str, Any] = {}

        if order_item_ids:
            params["order_item_ids"] = [int(item_id) for item_id in order_item_ids]

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [OrderHistory(**item) for item in (response or [])]
        else:
            raise TypeError("This method requires an asynchronous client")

    def get_finance(self) -> OrderFinance:
        """
        Get the finance information of this order.

        Returns the order level totals plus a ``transactionSummary`` of the
        transactions the marketplace has calculated for it, which is what the
        payout reconciliation matches an Odoo invoice against.

        Returns:
            The order's finance information
        """
        if not self.id:
            raise ValueError("Cannot get finance information without an order id")

        url = f"/v2/order/{self.id}/finance"

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return OrderFinance(**response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_finance_async(self) -> OrderFinance:
        """
        Get the finance information of this order, asynchronously.

        Returns:
            The order's finance information
        """
        if not self.id:
            raise ValueError("Cannot get finance information without an order id")

        url = f"/v2/order/{self.id}/finance"

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return OrderFinance(**response)
        else:
            raise TypeError("This method requires an asynchronous client")

    # ------------------------------------------------------------------
    # Write-back
    #
    # The Iconic API has no order level write endpoints at all: there is no
    # /v2/orders/{n}/status, /packed, /shipment or /cancel in the OpenAPI
    # contract and there never was. Everything below is a convenience wrapper
    # that fans the requested change out over the order's *items* through the
    # real endpoints on ``client.order_items``, and returns the order item ids
    # the API confirmed -- never an Order, because the 200 body of those
    # endpoints is ``{"orderItemIds": [...]}`` and rebuilding the Order model
    # from it would raise ValidationError after the write had already landed.
    # ------------------------------------------------------------------

    def _order_items_resource(self) -> OrderItemResource:
        """Return the item-level resource that owns the real write endpoints."""
        return getattr(self._client, "order_items", None) or OrderItemResource(client=self._client)

    def _resolve_order_item_ids(self, order_item_ids: Optional[List[int]] = None) -> List[int]:
        """
        Resolve the order items a write-back applies to.

        Args:
            order_item_ids: Explicit subset; defaults to every item of this order

        Returns:
            The order item ids to send
        """
        if order_item_ids:
            return [int(item_id) for item_id in order_item_ids]

        resolved = getattr(self._model, "orderItemIds", None) or self._data.get("orderItemIds")

        if not resolved:
            items = getattr(self._model, "items", None) or self._data.get("items") or []
            resolved = [
                item.get("id") if isinstance(item, dict) else getattr(item, "id", None)
                for item in items
            ]
            resolved = [item_id for item_id in resolved if item_id]

        if not resolved:
            raise ValueError(
                "Cannot resolve the order items of this order; fetch it with "
                "get_by_order_id() or pass order_item_ids explicitly"
            )

        return [int(item_id) for item_id in resolved]

    def _status_transition_call(
        self,
        status: str,
        order_item_ids: Optional[List[int]] = None,
        tracking_number: Optional[str] = None,
        shipping_provider: Optional[str] = None,
        delivery_type: Optional[DeliveryType] = None,
        reason: Optional[str] = None,
        reason_detail: Optional[str] = None,
    ) -> Tuple[str, Tuple[Any, ...], Dict[str, Any]]:
        """
        Resolve a target status to the item-level call that performs it.

        Args:
            status: Target order item status, or one of the aliases in
                    ``_STATUS_TRANSITIONS``
            order_item_ids: Explicit subset; defaults to every item of this order
            tracking_number: Tracking number, for the ready-to-ship / packed transitions
            shipping_provider: Provider name, for the ready-to-ship / packed transitions
            delivery_type: One of 'dropship', 'pickup', 'send_to_warehouse'
            reason: Failure reason name, for the cancel / fail / return transitions
            reason_detail: Additional information for that reason

        Returns:
            The ``OrderItemResource`` method name plus its positional and
            keyword arguments, so the sync and async twins can share the mapping
        """
        status_value = getattr(status, "value", status)
        method_name = self._STATUS_TRANSITIONS.get(status_value)

        if not method_name:
            raise ValueError(
                f"Unsupported target status {status_value!r}; expected one of "
                f"{sorted(self._STATUS_TRANSITIONS)}"
            )

        item_ids = self._resolve_order_item_ids(order_item_ids)

        if method_name == "set_to_ready_to_ship":
            return (
                method_name,
                ([{"id": item_id} for item_id in item_ids], tracking_number),
                {"delivery_type": delivery_type, "shipping_provider": shipping_provider},
            )

        if method_name == "set_to_packed_by_marketplace":
            return (
                method_name,
                ([{"orderItemId": item_id} for item_id in item_ids], delivery_type or "dropship"),
                {"shipping_provider": shipping_provider, "tracking_number": tracking_number},
            )

        if method_name in ("set_to_cancelled", "set_to_delivery_failed", "set_to_return_rejected"):
            return method_name, (item_ids, reason), {"reason_detail": reason_detail}

        if method_name == "set_to_returned":
            return method_name, (item_ids,), {"reason": reason}

        return method_name, (item_ids,), {}

    def update_status(
        self,
        status: str,
        order_item_ids: Optional[List[int]] = None,
        tracking_number: Optional[str] = None,
        shipping_provider: Optional[str] = None,
        delivery_type: Optional[DeliveryType] = None,
        reason: Optional[str] = None,
        reason_detail: Optional[str] = None,
    ) -> List[int]:
        """
        Move every item of this order to ``status``.

        There is no PUT /v2/orders/{orderNumber}/status endpoint and there never
        was one -- the API only transitions order items. This walks the order's
        items through the matching ``/v2/orders/statuses/set-to-*`` endpoint
        instead, which is why it returns order item ids rather than an Order.

        Args:
            status: Target status. 'ready_to_ship', 'packed_by_marketplace',
                    'shipped', 'delivered', 'canceled', 'failed', 'returned',
                    'return_approved', 'return_received' or 'return_rejected'
            order_item_ids: Explicit subset; defaults to every item of this order
            tracking_number: Required for 'ready_to_ship' unless the delivery
                             type is 'pickup'
            shipping_provider: Provider name, as listed by
                               ``client.order_items.get_shipment_providers()``
            delivery_type: One of 'dropship', 'pickup', 'send_to_warehouse'
            reason: Failure reason name, required for 'canceled', 'failed' and
                    'return_rejected'; valid values come from
                    ``client.order_items.get_failure_reasons()``
            reason_detail: Additional information for that reason

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")

        method_name, args, kwargs = self._status_transition_call(
            status,
            order_item_ids=order_item_ids,
            tracking_number=tracking_number,
            shipping_provider=shipping_provider,
            delivery_type=delivery_type,
            reason=reason,
            reason_detail=reason_detail,
        )

        return getattr(self._order_items_resource(), method_name)(*args, **kwargs)

    async def update_status_async(
        self,
        status: str,
        order_item_ids: Optional[List[int]] = None,
        tracking_number: Optional[str] = None,
        shipping_provider: Optional[str] = None,
        delivery_type: Optional[DeliveryType] = None,
        reason: Optional[str] = None,
        reason_detail: Optional[str] = None,
    ) -> List[int]:
        """
        Move every item of this order to ``status``, asynchronously.

        Args:
            See update_status for available parameters

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")

        method_name, args, kwargs = self._status_transition_call(
            status,
            order_item_ids=order_item_ids,
            tracking_number=tracking_number,
            shipping_provider=shipping_provider,
            delivery_type=delivery_type,
            reason=reason,
            reason_detail=reason_detail,
        )

        return await getattr(self._order_items_resource(), f"{method_name}_async")(*args, **kwargs)

    def mark_as_packed(
        self,
        delivery_type: DeliveryType = "dropship",
        shipping_provider: Optional[str] = None,
        tracking_number: Optional[str] = None,
        order_item_ids: Optional[List[int]] = None,
    ) -> List[int]:
        """
        Mark every item of this order as packed by the marketplace.

        There is no PUT /v2/orders/{orderNumber}/packed endpoint and there never
        was one. This posts to /v2/orders/statuses/set-to-packed-by-marketplace
        instead, which needs a delivery type -- hence the 'dropship' default,
        which keeps the historic no-argument call working.

        The items stay ``pending``; only the packed flag moves.

        Args:
            delivery_type: One of 'dropship', 'pickup', 'send_to_warehouse'
            shipping_provider: Provider name, mandatory for drop-shipping
            tracking_number: Required when the provider has no API integration
            order_item_ids: Explicit subset; defaults to every item of this order

        Returns:
            The order item IDs the API confirmed as packed
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")

        item_ids = self._resolve_order_item_ids(order_item_ids)

        return self._order_items_resource().set_to_packed_by_marketplace(
            [{"orderItemId": item_id} for item_id in item_ids],
            delivery_type,
            shipping_provider=shipping_provider,
            tracking_number=tracking_number,
        )

    async def mark_as_packed_async(
        self,
        delivery_type: DeliveryType = "dropship",
        shipping_provider: Optional[str] = None,
        tracking_number: Optional[str] = None,
        order_item_ids: Optional[List[int]] = None,
    ) -> List[int]:
        """
        Mark every item of this order as packed by the marketplace, asynchronously.

        Args:
            See mark_as_packed for available parameters

        Returns:
            The order item IDs the API confirmed as packed
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")

        item_ids = self._resolve_order_item_ids(order_item_ids)

        return await self._order_items_resource().set_to_packed_by_marketplace_async(
            [{"orderItemId": item_id} for item_id in item_ids],
            delivery_type,
            shipping_provider=shipping_provider,
            tracking_number=tracking_number,
        )

    def update_shipment(
        self,
        tracking_number: str,
        shipping_provider: str,
        shipping_type: Optional[str] = None,
        order_item_ids: Optional[List[int]] = None,
    ) -> List[int]:
        """
        Update the shipping provider and tracking code of this order's items.

        There is no PUT /v2/orders/{orderNumber}/shipment endpoint and there
        never was one. This posts to /v2/order-item/{orderItemId}/shipping-provider
        once per item instead. That endpoint already propagates the change to
        every item in the same package, so repeating it for the order's other
        items is redundant rather than harmful, and it only applies to items
        that are ``ready_to_ship``.

        ``shipping_type`` is accepted for backwards compatibility and ignored:
        neither the shipping-provider nor the tracking-code endpoint has such a
        field.

        Args:
            tracking_number: The actual tracking code of the package
            shipping_provider: Provider name, as listed by
                               ``client.order_items.get_shipment_providers()``
            shipping_type: Ignored; kept so existing callers keep working
            order_item_ids: Explicit subset; defaults to every item of this order

        Returns:
            The order item IDs whose shipping information was updated
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")

        if not shipping_provider:
            raise ValueError("Cannot update shipment without a shipping provider")

        order_items = self._order_items_resource()
        updated: List[int] = []

        for item_id in self._resolve_order_item_ids(order_item_ids):
            order_items.set_shipping_provider(
                item_id, shipping_provider, tracking_code=tracking_number
            )
            updated.append(item_id)

        return updated

    async def update_shipment_async(
        self,
        tracking_number: str,
        shipping_provider: str,
        shipping_type: Optional[str] = None,
        order_item_ids: Optional[List[int]] = None,
    ) -> List[int]:
        """
        Update the shipping provider and tracking code of this order's items, asynchronously.

        Args:
            See update_shipment for available parameters

        Returns:
            The order item IDs whose shipping information was updated
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")

        if not shipping_provider:
            raise ValueError("Cannot update shipment without a shipping provider")

        order_items = self._order_items_resource()
        updated: List[int] = []

        for item_id in self._resolve_order_item_ids(order_item_ids):
            await order_items.set_shipping_provider_async(
                item_id, shipping_provider, tracking_code=tracking_number
            )
            updated.append(item_id)

        return updated

    def cancel(
        self,
        reason: str,
        reason_detail: Optional[str] = None,
        order_item_ids: Optional[List[int]] = None,
    ) -> List[int]:
        """
        Cancel every item of this order.

        There is no PUT /v2/orders/{orderNumber}/cancel endpoint and there never
        was one. This posts to /v2/orders/statuses/set-to-cancelled instead,
        which only accepts items that are ``pending`` or ``ready_to_ship``.

        Args:
            reason: Failure reason name. It must be one of the names returned by
                    ``client.order_items.get_failure_reasons()``; free text is
                    rejected with a validation error
            reason_detail: Additional information
            order_item_ids: Explicit subset; defaults to every item of this order

        Returns:
            The order item IDs the API confirmed as cancelled
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")

        item_ids = self._resolve_order_item_ids(order_item_ids)

        return self._order_items_resource().set_to_cancelled(
            item_ids, reason, reason_detail=reason_detail
        )

    async def cancel_async(
        self,
        reason: str,
        reason_detail: Optional[str] = None,
        order_item_ids: Optional[List[int]] = None,
    ) -> List[int]:
        """
        Cancel every item of this order, asynchronously.

        Args:
            See cancel for available parameters

        Returns:
            The order item IDs the API confirmed as cancelled
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")

        item_ids = self._resolve_order_item_ids(order_item_ids)

        return await self._order_items_resource().set_to_cancelled_async(
            item_ids, reason, reason_detail=reason_detail
        )

    def list_finance_transactions(self) -> List["Transaction"]:
        """List financial transactions associated with this order."""
        if not self._data.get("number"):
            raise ValueError("Cannot list transactions without an order number")
        
        finance_client: Finance = self._client.finance
        
        return finance_client.list_transactions(order_numbers=[self._data["number"]])
    
    def bulk_fetch_transactions(self, orders: List["Order"]) -> List["BulkFetchTransactionsData"]:
        """Bulk fetch transactions for a list of orders and return a list of dictionaries with order and transactions."""
        
        finance_client: Finance = self._client.finance

        all_transactions = []
        for chunk in utils.chunks(orders, 100):
            all_transactions.extend(finance_client.paginate_transactions(order_numbers=[order.number for order in chunk]))
            
        transactions_by_order = {}
        for order in orders:
            transactions_by_order[order] = [
                transaction for transaction in all_transactions if transaction.orderNumber == order.number
            ]
            
        return [
            BulkFetchTransactionsData(order=order, transactions=transactions_by_order[order])
            for order in orders
        ]