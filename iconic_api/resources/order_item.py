from typing import Dict, Any, List, Optional, Union, Literal

from .base import IconicResource
from ..models import (
    OrderItem as OrderItemModel,
    OrderItemReturn,
)

#: The three delivery types the order status endpoints accept.
#: Spec: ``deliveryType`` enum on POST /v2/orders/statuses/set-to-ready-to-ship
#: and POST /v2/orders/statuses/set-to-packed-by-marketplace.
DeliveryType = Literal["dropship", "pickup", "send_to_warehouse"]

DELIVERY_TYPES = ("dropship", "pickup", "send_to_warehouse")


class OrderItemResource(IconicResource):
    """
    Order item resource: the real write-back surface of the orders API.

    The Iconic API transitions **order items**, never orders. Every status
    change is a POST to ``/v2/orders/statuses/set-to-<status>`` carrying a
    collection of order item ids, and every one of them answers with
    ``{"orderItemIds": [...]}`` -- not with an order. The ``set_to_*`` methods
    below therefore return a plain ``List[int]``; wrapping the response in an
    :class:`~iconic_api.resources.order.Order` would raise ``ValidationError``
    *after* the write had already landed.

    All order items passed to a single ``set_to_*`` call must belong to the
    **same order**. Nothing here enforces that -- the API rejects a mixed batch
    with a 422 -- so callers must group their items per order first.
    """

    endpoint = "order-items"
    model_class = None  # Responses are returned as pydantic models or plain ids

    # ------------------------------------------------------------------
    # Payload helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_order_items(
        order_items: List[Union[int, Dict[str, Any]]],
        id_key: str,
    ) -> List[Dict[str, Any]]:
        """
        Normalise an ``orderItems`` collection onto the key the endpoint wants.

        The two package-forming endpoints disagree on the item key:
        ``set-to-ready-to-ship`` expects ``{"id": ...}`` while
        ``set-to-packed-by-marketplace`` expects ``{"orderItemId": ...}``.
        Sending the wrong one is silently accepted as "no items", so the key is
        applied here rather than trusted from the caller.

        Args:
            order_items: Items to transition. Each entry is either a bare order
                         item id or a dict carrying the id under any of ``id`` /
                         ``orderItemId`` plus an optional ``serialNumber``
            id_key: ``"id"`` or ``"orderItemId"``, per the endpoint

        Returns:
            The ``orderItems`` array, keyed as the endpoint expects
        """
        if not order_items:
            raise ValueError("Cannot transition order items without any order items")

        normalised: List[Dict[str, Any]] = []
        for item in order_items:
            if isinstance(item, dict):
                item_id = item.get(id_key)
                if item_id is None:
                    item_id = item.get("id", item.get("orderItemId"))
                serial_number = item.get("serialNumber", item.get("serial_number"))
            else:
                item_id = item
                serial_number = None

            if item_id is None:
                raise ValueError(f"Order item {item!r} carries no order item id")

            entry: Dict[str, Any] = {id_key: int(item_id)}
            if serial_number:
                entry["serialNumber"] = serial_number
            normalised.append(entry)

        return normalised

    @staticmethod
    def _normalise_order_item_ids(order_item_ids: List[int]) -> List[int]:
        """
        Coerce an ``orderItemIds`` collection to a non-empty list of ints.

        Args:
            order_item_ids: Order item ids to transition

        Returns:
            The ids as plain ints, ready to be JSON encoded
        """
        if not order_item_ids:
            raise ValueError("Cannot transition order items without any order item ids")

        return [int(order_item_id) for order_item_id in order_item_ids]

    @staticmethod
    def _validate_delivery_type(delivery_type: Optional[str]) -> Optional[str]:
        """
        Reject a delivery type the API does not know about.

        Args:
            delivery_type: One of 'dropship', 'pickup', 'send_to_warehouse', or None

        Returns:
            The delivery type unchanged
        """
        if delivery_type is not None and delivery_type not in DELIVERY_TYPES:
            raise ValueError(
                f"Invalid deliveryType {delivery_type!r}; expected one of {DELIVERY_TYPES}"
            )

        return delivery_type

    @staticmethod
    def _extract_order_item_ids(response: Any) -> List[int]:
        """
        Pull the confirmed order item ids out of a ``set-to-*`` response.

        The transport hands back ``{}`` for an empty 2xx body (client.py:236),
        so a missing key is treated as "nothing confirmed" rather than an error.

        Args:
            response: The decoded 200 body

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        if isinstance(response, dict):
            return [int(order_item_id) for order_item_id in (response.get("orderItemIds") or [])]
        if isinstance(response, list):
            return [int(order_item_id) for order_item_id in response]

        return []

    def _ready_to_ship_payload(
        self,
        order_items: List[Union[int, Dict[str, Any]]],
        tracking_number: Optional[str],
        delivery_type: Optional[DeliveryType],
        shipping_provider: Optional[str],
        access_key: Optional[str],
        document_url: Optional[str],
        invoice_encoded_xml: Optional[str],
    ) -> Dict[str, Any]:
        """Build the POST /v2/orders/statuses/set-to-ready-to-ship body."""
        self._validate_delivery_type(delivery_type)

        # trackingNumber is a required property of the request schema; the only
        # documented exception is a 'pickup' delivery, where the marketplace
        # collects the package and no tracking number exists yet.
        if not tracking_number and delivery_type != "pickup":
            raise ValueError(
                "trackingNumber is required by set-to-ready-to-ship unless deliveryType is 'pickup'"
            )

        payload: Dict[str, Any] = {
            "orderItems": self._normalise_order_items(order_items, "id"),
        }

        if tracking_number:
            payload["trackingNumber"] = tracking_number
        if delivery_type:
            payload["deliveryType"] = delivery_type
        if shipping_provider:
            payload["shippingProvider"] = shipping_provider
        if access_key:
            payload["accessKey"] = access_key
        if document_url:
            payload["documentUrl"] = document_url
        if invoice_encoded_xml:
            payload["invoiceEncodedXml"] = invoice_encoded_xml

        return payload

    def _packed_by_marketplace_payload(
        self,
        order_items: List[Union[int, Dict[str, Any]]],
        delivery_type: DeliveryType,
        shipping_provider: Optional[str],
        tracking_number: Optional[str],
    ) -> Dict[str, Any]:
        """Build the POST /v2/orders/statuses/set-to-packed-by-marketplace body."""
        if not delivery_type:
            raise ValueError("deliveryType is required by set-to-packed-by-marketplace")

        self._validate_delivery_type(delivery_type)

        payload: Dict[str, Any] = {
            "orderItems": self._normalise_order_items(order_items, "orderItemId"),
            "deliveryType": delivery_type,
        }

        if shipping_provider:
            payload["shippingProvider"] = shipping_provider
        if tracking_number:
            payload["trackingNumber"] = tracking_number

        return payload

    def _order_item_ids_payload(
        self,
        order_item_ids: List[int],
        reason: Optional[str] = None,
        reason_detail: Optional[str] = None,
        reason_required: bool = False,
    ) -> Dict[str, Any]:
        """
        Build the ``{"orderItemIds": [...]}`` body shared by eight endpoints.

        Args:
            order_item_ids: Order item ids to transition
            reason: Failure reason name, as listed by GET /v2/orders-failure-reasons
            reason_detail: Free-text detail attached to the reason
            reason_required: True where the request schema marks ``reason`` required

        Returns:
            The request body
        """
        if reason_required and not reason:
            raise ValueError(
                "reason is required; valid values come from GET /v2/orders-failure-reasons"
            )

        payload: Dict[str, Any] = {
            "orderItemIds": self._normalise_order_item_ids(order_item_ids),
        }

        if reason:
            payload["reason"] = reason
        if reason_detail:
            payload["reasonDetail"] = reason_detail

        return payload

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def list_order_items(self, **params) -> List[OrderItemModel]:
        """
        Receive an order item collection based on search parameters.

        ``limit`` and ``offset`` are required query parameters of
        GET /v2/order-items and default to a single 100 item page here.

        Args:
            order_item_ids: Array of numeric order item ids
            order_ids: Array of numeric order ids
            order_numbers: Array of order numbers
            created_at_start: Filter by created at range
            created_at_end: Filter by created at range
            updated_at_start: Filter by updated at range
            updated_at_end: Filter by updated at range
            status: Filter by status
            returned_by: 'seller' or 'region'
            src_ids: Filter by srcId
            sort: Sorting field ('updatedAt')
            sort_dir: Sorting direction ('asc', 'desc')
            include_voucher_details: Include voucher details in the response
            shipment_type: 'warehouse', 'dropshipping' or 'crossdocking'
            limit: Maximum number of items to return
            offset: Starting point in the collection

        Returns:
            The matching order items
        """
        url = "/v2/order-items"

        params.setdefault("limit", 100)
        params.setdefault("offset", 0)

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [OrderItemModel(**item) for item in self._extract_items(response)]
        else:
            raise TypeError("This method requires a synchronous client")

    async def list_order_items_async(self, **params) -> List[OrderItemModel]:
        """
        Receive an order item collection based on search parameters, asynchronously.

        Args:
            See list_order_items for available parameters

        Returns:
            The matching order items
        """
        url = "/v2/order-items"

        params.setdefault("limit", 100)
        params.setdefault("offset", 0)

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [OrderItemModel(**item) for item in self._extract_items(response)]
        else:
            raise TypeError("This method requires an asynchronous client")

    def get_returns(self, order_item_ids: Optional[List[int]] = None) -> List[OrderItemReturn]:
        """
        Get the return package information for the given order items.

        Args:
            order_item_ids: Array of numeric order item ids

        Returns:
            One return record per order item that has one
        """
        url = "/v2/order-items/returns"
        params: Dict[str, Any] = {}

        if order_item_ids:
            params["order_item_ids"] = self._normalise_order_item_ids(order_item_ids)

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [OrderItemReturn(**item) for item in (response or [])]
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_returns_async(self, order_item_ids: Optional[List[int]] = None) -> List[OrderItemReturn]:
        """
        Get the return package information for the given order items, asynchronously.

        Args:
            order_item_ids: Array of numeric order item ids

        Returns:
            One return record per order item that has one
        """
        url = "/v2/order-items/returns"
        params: Dict[str, Any] = {}

        if order_item_ids:
            params["order_item_ids"] = self._normalise_order_item_ids(order_item_ids)

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [OrderItemReturn(**item) for item in (response or [])]
        else:
            raise TypeError("This method requires an asynchronous client")

    def get_shipment_providers(self, status: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Get the shipment providers available to this seller.

        The ``name`` of a provider is what ``shippingProvider`` expects on the
        ready-to-ship / packed-by-marketplace calls, and
        ``apiIntegrationAvailable`` says whether a tracking number has to be
        supplied by us or is allocated by the provider.

        Args:
            status: Filter by the provider's status for this seller

        Returns:
            The shipment providers, as returned by the API
        """
        url = "/v2/orders-shipment-providers"
        params: Dict[str, Any] = {}

        if status is not None:
            params["status"] = status

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return response or []
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_shipment_providers_async(self, status: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Get the shipment providers available to this seller, asynchronously.

        Args:
            status: Filter by the provider's status for this seller

        Returns:
            The shipment providers, as returned by the API
        """
        url = "/v2/orders-shipment-providers"
        params: Dict[str, Any] = {}

        if status is not None:
            params["status"] = status

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return response or []
        else:
            raise TypeError("This method requires an asynchronous client")

    def get_failure_reasons(self) -> List[Dict[str, Any]]:
        """
        Get the active failure reasons for orders.

        The ``name`` of a reason is the value the ``reason`` field expects on
        set-to-cancelled, set-to-delivery-failed, set-to-returned and
        set-to-return-rejected; ``type`` says which of those a reason is legal
        for.

        Returns:
            The failure reasons, as returned by the API
        """
        url = "/v2/orders-failure-reasons"

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return response or []
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_failure_reasons_async(self) -> List[Dict[str, Any]]:
        """
        Get the active failure reasons for orders, asynchronously.

        Returns:
            The failure reasons, as returned by the API
        """
        url = "/v2/orders-failure-reasons"

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return response or []
        else:
            raise TypeError("This method requires an asynchronous client")

    # ------------------------------------------------------------------
    # Status transitions (POST /v2/orders/statuses/set-to-*)
    # ------------------------------------------------------------------

    def set_to_ready_to_ship(
        self,
        order_items: List[Union[int, Dict[str, Any]]],
        tracking_number: str,
        delivery_type: Optional[DeliveryType] = None,
        shipping_provider: Optional[str] = None,
        access_key: Optional[str] = None,
        document_url: Optional[str] = None,
        invoice_encoded_xml: Optional[str] = None,
    ) -> List[int]:
        """
        Move order items to ``ready_to_ship``, packing them into one package.

        All items in a single call must belong to the same order and must
        currently be ``pending``. The tracking number must be unique and cannot
        be spread over several packages.

        Args:
            order_items: Items to pack, each ``{"id": <order item id>}`` with an
                         optional ``"serialNumber"``; bare ids are accepted too
            tracking_number: Tracking number for the package. Required by the
                             API unless ``delivery_type`` is 'pickup'
            delivery_type: One of 'dropship', 'pickup', 'send_to_warehouse'
            shipping_provider: Shipment provider name, as listed by
                               ``get_shipment_providers()``
            access_key: Invoice access key; taken from ``invoice_encoded_xml`` when empty
            document_url: URL pointing at the document
            invoice_encoded_xml: The invoice as base64 encoded XML

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-ready-to-ship"

        payload = self._ready_to_ship_payload(
            order_items,
            tracking_number,
            delivery_type,
            shipping_provider,
            access_key,
            document_url,
            invoice_encoded_xml,
        )

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_to_ready_to_ship_async(
        self,
        order_items: List[Union[int, Dict[str, Any]]],
        tracking_number: str,
        delivery_type: Optional[DeliveryType] = None,
        shipping_provider: Optional[str] = None,
        access_key: Optional[str] = None,
        document_url: Optional[str] = None,
        invoice_encoded_xml: Optional[str] = None,
    ) -> List[int]:
        """
        Move order items to ``ready_to_ship`` asynchronously.

        All items in a single call must belong to the same order.

        Args:
            See set_to_ready_to_ship for available parameters

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-ready-to-ship"

        payload = self._ready_to_ship_payload(
            order_items,
            tracking_number,
            delivery_type,
            shipping_provider,
            access_key,
            document_url,
            invoice_encoded_xml,
        )

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def set_to_packed_by_marketplace(
        self,
        order_items: List[Union[int, Dict[str, Any]]],
        delivery_type: DeliveryType,
        shipping_provider: Optional[str] = None,
        tracking_number: Optional[str] = None,
    ) -> List[int]:
        """
        Mark order items as packed by the marketplace.

        The real status stays ``pending``; only the packed flag moves. All items
        in a single call must belong to the same order, must currently be
        ``pending`` and must not be digital.

        Note the item key: this endpoint wants ``{"orderItemId": ...}`` where
        set-to-ready-to-ship wants ``{"id": ...}``. Both spellings are accepted
        here and rewritten to the one the endpoint expects.

        Args:
            order_items: Items to pack, each ``{"orderItemId": <order item id>}``
                         with an optional ``"serialNumber"``; bare ids are
                         accepted too
            delivery_type: One of 'dropship', 'pickup', 'send_to_warehouse'.
                           Required by this endpoint
            shipping_provider: Shipment provider name, as listed by
                               ``get_shipment_providers()``. Mandatory for
                               drop-shipping
            tracking_number: Required when the shipment provider has no API
                             integration

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-packed-by-marketplace"

        payload = self._packed_by_marketplace_payload(
            order_items,
            delivery_type,
            shipping_provider,
            tracking_number,
        )

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_to_packed_by_marketplace_async(
        self,
        order_items: List[Union[int, Dict[str, Any]]],
        delivery_type: DeliveryType,
        shipping_provider: Optional[str] = None,
        tracking_number: Optional[str] = None,
    ) -> List[int]:
        """
        Mark order items as packed by the marketplace, asynchronously.

        All items in a single call must belong to the same order.

        Args:
            See set_to_packed_by_marketplace for available parameters

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-packed-by-marketplace"

        payload = self._packed_by_marketplace_payload(
            order_items,
            delivery_type,
            shipping_provider,
            tracking_number,
        )

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def set_to_shipped(self, order_item_ids: List[int]) -> List[int]:
        """
        Move order items to ``shipped``.

        All items in a single call must belong to the same order and must be
        ``ready_to_ship``. Items with a CrossDocking shipment type cannot make
        this transition.

        Args:
            order_item_ids: Order item ids to transition

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-shipped"

        payload = self._order_item_ids_payload(order_item_ids)

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_to_shipped_async(self, order_item_ids: List[int]) -> List[int]:
        """
        Move order items to ``shipped`` asynchronously.

        All items in a single call must belong to the same order.

        Args:
            order_item_ids: Order item ids to transition

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-shipped"

        payload = self._order_item_ids_payload(order_item_ids)

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def set_to_delivered(self, order_item_ids: List[int]) -> List[int]:
        """
        Move order items to ``delivered``.

        All items in a single call must belong to the same order and must be
        ``shipped`` or already ``delivered``. Only applicable to dropshipping.

        Args:
            order_item_ids: Order item ids to transition

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-delivered"

        payload = self._order_item_ids_payload(order_item_ids)

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_to_delivered_async(self, order_item_ids: List[int]) -> List[int]:
        """
        Move order items to ``delivered`` asynchronously.

        All items in a single call must belong to the same order.

        Args:
            order_item_ids: Order item ids to transition

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-delivered"

        payload = self._order_item_ids_payload(order_item_ids)

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def set_to_cancelled(
        self,
        order_item_ids: List[int],
        reason: str,
        reason_detail: Optional[str] = None,
    ) -> List[int]:
        """
        Move order items to ``canceled``.

        All items in a single call must belong to the same order and must be
        ``pending`` or ``ready_to_ship``. Cancelling one item can cancel the
        whole package.

        Args:
            order_item_ids: Order item ids to transition
            reason: Failure reason name, as listed by ``get_failure_reasons()``.
                    An unknown reason is a validation error
            reason_detail: Additional information

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-cancelled"

        payload = self._order_item_ids_payload(
            order_item_ids, reason, reason_detail, reason_required=True
        )

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_to_cancelled_async(
        self,
        order_item_ids: List[int],
        reason: str,
        reason_detail: Optional[str] = None,
    ) -> List[int]:
        """
        Move order items to ``canceled`` asynchronously.

        All items in a single call must belong to the same order.

        Args:
            See set_to_cancelled for available parameters

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-cancelled"

        payload = self._order_item_ids_payload(
            order_item_ids, reason, reason_detail, reason_required=True
        )

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def set_to_delivery_failed(
        self,
        order_item_ids: List[int],
        reason: str,
        reason_detail: Optional[str] = None,
    ) -> List[int]:
        """
        Move order items to ``failed`` delivery.

        All items in a single call must belong to the same order and must be
        ``shipped``.

        Args:
            order_item_ids: Order item ids to transition
            reason: Failure reason name, as listed by ``get_failure_reasons()``
            reason_detail: Additional information

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-delivery-failed"

        payload = self._order_item_ids_payload(
            order_item_ids, reason, reason_detail, reason_required=True
        )

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_to_delivery_failed_async(
        self,
        order_item_ids: List[int],
        reason: str,
        reason_detail: Optional[str] = None,
    ) -> List[int]:
        """
        Move order items to ``failed`` delivery asynchronously.

        All items in a single call must belong to the same order.

        Args:
            See set_to_delivery_failed for available parameters

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-delivery-failed"

        payload = self._order_item_ids_payload(
            order_item_ids, reason, reason_detail, reason_required=True
        )

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def set_to_returned(
        self,
        order_item_ids: List[int],
        reason: Optional[str] = None,
    ) -> List[int]:
        """
        Move order items to ``returned``.

        All items in a single call must belong to the same order and must be
        ``delivered``.

        Args:
            order_item_ids: Order item ids to transition
            reason: Optional failure reason name, as listed by ``get_failure_reasons()``

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-returned"

        payload = self._order_item_ids_payload(order_item_ids, reason)

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_to_returned_async(
        self,
        order_item_ids: List[int],
        reason: Optional[str] = None,
    ) -> List[int]:
        """
        Move order items to ``returned`` asynchronously.

        All items in a single call must belong to the same order.

        Args:
            See set_to_returned for available parameters

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-returned"

        payload = self._order_item_ids_payload(order_item_ids, reason)

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def set_to_return_approved(self, order_item_ids: List[int]) -> List[int]:
        """
        Approve the return of order items.

        All items in a single call must belong to the same order and must be
        ``return_waiting_for_approval``. The seller setting "Manage Returns"
        must be "Seller can receive returned items from warehouse".

        Args:
            order_item_ids: Order item ids to transition

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-return-approved"

        payload = self._order_item_ids_payload(order_item_ids)

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_to_return_approved_async(self, order_item_ids: List[int]) -> List[int]:
        """
        Approve the return of order items asynchronously.

        All items in a single call must belong to the same order.

        Args:
            order_item_ids: Order item ids to transition

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-return-approved"

        payload = self._order_item_ids_payload(order_item_ids)

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def set_to_return_received(self, order_item_ids: List[int]) -> List[int]:
        """
        Mark the return of order items as received.

        All items in a single call must belong to the same order and must be
        ``return_shipped_by_customer``.

        Args:
            order_item_ids: Order item ids to transition

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-return-received"

        payload = self._order_item_ids_payload(order_item_ids)

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_to_return_received_async(self, order_item_ids: List[int]) -> List[int]:
        """
        Mark the return of order items as received, asynchronously.

        All items in a single call must belong to the same order.

        Args:
            order_item_ids: Order item ids to transition

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-return-received"

        payload = self._order_item_ids_payload(order_item_ids)

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def set_to_return_rejected(
        self,
        order_item_ids: List[int],
        reason: str,
        reason_detail: Optional[str] = None,
    ) -> List[int]:
        """
        Reject the return of order items.

        All items in a single call must belong to the same order and must be
        ``return_waiting_for_approval``. The seller setting "Manage Returns"
        must be "Seller can receive returned items from customer".

        Args:
            order_item_ids: Order item ids to transition
            reason: Rejection reason name, as listed by ``get_failure_reasons()``
            reason_detail: Additional information

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-return-rejected"

        payload = self._order_item_ids_payload(
            order_item_ids, reason, reason_detail, reason_required=True
        )

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_to_return_rejected_async(
        self,
        order_item_ids: List[int],
        reason: str,
        reason_detail: Optional[str] = None,
    ) -> List[int]:
        """
        Reject the return of order items asynchronously.

        All items in a single call must belong to the same order.

        Args:
            See set_to_return_rejected for available parameters

        Returns:
            The order item IDs the API confirmed as transitioned
        """
        url = "/v2/orders/statuses/set-to-return-rejected"

        payload = self._order_item_ids_payload(
            order_item_ids, reason, reason_detail, reason_required=True
        )

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=payload)
            return self._extract_order_item_ids(response)
        else:
            raise TypeError("This method requires an asynchronous client")

    # ------------------------------------------------------------------
    # Per-item shipping details
    # ------------------------------------------------------------------

    def set_tracking_code(self, order_item_id: int, tracking_code: str) -> Dict[str, Any]:
        """
        Update the tracking code of an order item that is ``ready_to_ship``.

        The change applies to every item in the same package, so it only has to
        be sent once per package.

        Args:
            order_item_id: Numeric order item id
            tracking_code: The actual tracking code of the package

        Returns:
            The (empty) acknowledgement body
        """
        if not order_item_id:
            raise ValueError("Cannot set a tracking code without an order item id")
        if not tracking_code:
            raise ValueError("Cannot set an empty tracking code")

        url = f"/v2/order-item/{order_item_id}/tracking-code"
        payload = {"trackingCode": tracking_code}

        if hasattr(self._client, '_make_request_sync'):
            return self._client._make_request_sync("POST", url, json_data=payload)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_tracking_code_async(self, order_item_id: int, tracking_code: str) -> Dict[str, Any]:
        """
        Update the tracking code of an order item asynchronously.

        Args:
            order_item_id: Numeric order item id
            tracking_code: The actual tracking code of the package

        Returns:
            The (empty) acknowledgement body
        """
        if not order_item_id:
            raise ValueError("Cannot set a tracking code without an order item id")
        if not tracking_code:
            raise ValueError("Cannot set an empty tracking code")

        url = f"/v2/order-item/{order_item_id}/tracking-code"
        payload = {"trackingCode": tracking_code}

        if hasattr(self._client, '_make_request_async'):
            return await self._client._make_request_async("POST", url, json_data=payload)
        else:
            raise TypeError("This method requires an asynchronous client")

    def set_shipping_provider(
        self,
        order_item_id: int,
        shipping_provider: str,
        tracking_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update the shipping provider of an order item that is ``ready_to_ship``.

        The change applies to every item in the same package, so it only has to
        be sent once per package.

        The 200 body is the full order item. It is returned as a plain dict
        rather than an ``OrderItem`` model: the write has already landed by the
        time it arrives, and a schema mismatch must not be reported as a failed
        write-back.

        Args:
            order_item_id: Numeric order item id
            shipping_provider: Provider name, as listed by ``get_shipment_providers()``
            tracking_code: The actual tracking code of the package

        Returns:
            The updated order item, as returned by the API
        """
        if not order_item_id:
            raise ValueError("Cannot set a shipping provider without an order item id")
        if not shipping_provider:
            raise ValueError("Cannot set an empty shipping provider")

        url = f"/v2/order-item/{order_item_id}/shipping-provider"
        payload: Dict[str, Any] = {"shippingProvider": shipping_provider}

        if tracking_code:
            payload["trackingCode"] = tracking_code

        if hasattr(self._client, '_make_request_sync'):
            return self._client._make_request_sync("POST", url, json_data=payload)
        else:
            raise TypeError("This method requires a synchronous client")

    async def set_shipping_provider_async(
        self,
        order_item_id: int,
        shipping_provider: str,
        tracking_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update the shipping provider of an order item asynchronously.

        Args:
            See set_shipping_provider for available parameters

        Returns:
            The updated order item, as returned by the API
        """
        if not order_item_id:
            raise ValueError("Cannot set a shipping provider without an order item id")
        if not shipping_provider:
            raise ValueError("Cannot set an empty shipping provider")

        url = f"/v2/order-item/{order_item_id}/shipping-provider"
        payload: Dict[str, Any] = {"shippingProvider": shipping_provider}

        if tracking_code:
            payload["trackingCode"] = tracking_code

        if hasattr(self._client, '_make_request_async'):
            return await self._client._make_request_async("POST", url, json_data=payload)
        else:
            raise TypeError("This method requires an asynchronous client")
