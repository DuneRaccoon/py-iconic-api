import datetime
from typing import Optional, List, Literal, Any, Dict, Union
from .base_api_module import BaseAPIModule
from ..models import (
    Order, 
    OrderStatus,
    SetInvoiceNumber,
    ListOrdersRequest
) # Import Pydantic models

class OrdersAPI(BaseAPIModule):
    
    def list_orders(self, params: ListOrdersRequest) -> List[Order]:
        """Get list of orders with filters."""
        headers = {}
        if params.x_context:
            headers["X-Context"] = params.x_context
        response_data = self._client._make_request_sync("GET", "/v2/orders", params=params.to_api_params(), headers=headers) # type: ignore
        return [Order(**item) for item in response_data]

    async def list_orders_async(self, params: ListOrdersRequest) -> List[Order]:
        """Get list of orders with filters (async)."""
        headers = {}
        if params.x_context:
            headers["X-Context"] = params.x_context
        response_data = await self._client._make_request_async("GET", "/v2/orders", params=params.to_api_params(), headers=headers)
        return [Order(**item) for item in response_data]

    def get_order_by_id(self, order_id: int) -> Order:
        """Get a specific order by ID."""
        response_data = self._client._make_request_sync("GET", f"/v2/orders/{order_id}") # type: ignore
        return Order(**response_data)

    async def get_order_by_id_async(self, order_id: int) -> Order:
        """Get a specific order by ID (async)."""
        response_data = await self._client._make_request_async("GET", f"/v2/orders/{order_id}") # type: ignore
        return Order(**response_data)

    def set_invoice_number(self, payload: SetInvoiceNumber) -> SetInvoiceNumber:
        """Sets an invoice number."""
        # Pydantic model .model_dump(by_alias=True) is useful here
        response_data = self._client._make_request_sync( # type: ignore
            "POST", 
            "/v2/orders/set-invoice-number", 
            json_data=payload.model_dump(by_alias=True, exclude_none=True)
        )
        return SetInvoiceNumber(**response_data)

    async def set_invoice_number_async(self, payload: SetInvoiceNumber) -> SetInvoiceNumber:
        """Sets an invoice number (async)."""
        response_data = await self._client._make_request_async( # type: ignore
            "POST", 
            "/v2/orders/set-invoice-number", 
            json_data=payload.model_dump(by_alias=True, exclude_none=True)
        )
        return SetInvoiceNumber(**response_data)

    def set_status(self, order: Order, status: OrderStatus) -> Dict[str, List[int]]:
        """Change status to ready to ship for order items."""
        new_order_status = f"status_{status.value}"
        preceeding_status = status.get_preceeding_status()
        if not preceeding_status:
            raise ValueError(f"Invalid status transition from {order.status} to {status}")
        
        for item in order.items:
            if item.status != preceeding_status:
                raise ValueError(f"Item {item.id} status {item.status} does not match expected {preceeding_status}")
            
        # Map OrderStatus to the appropriate method
        if status == OrderStatus.ready_to_ship:
            # This is the original behavior, ready to ship needs special handling
            return self._client._make_request_sync(
                "POST",
                "/v2/orders/statuses/set-to-ready-to-ship",
                # json_data=payload.model_dump(by_alias=True, exclude_none=True)
            )
        else:
            raise ValueError(f"Status transition to {status} not implemented in set_status method")

    async def set_status_async(self, order: Order, status: OrderStatus) -> Dict[str, List[int]]:
        """Change status to ready to ship for order items (async)."""
        preceeding_status = status.get_preceeding_status()
        if not preceeding_status:
            raise ValueError(f"Invalid status transition from {order.status} to {status}")
        
        for item in order.items:
            if item.status != preceeding_status:
                raise ValueError(f"Item {item.id} status {item.status} does not match expected {preceeding_status}")
            
        # Map OrderStatus to the appropriate method
        if status == OrderStatus.ready_to_ship:
            # This is the original behavior, ready to ship needs special handling
            return await self._client._make_request_async(
                "POST",
                "/v2/orders/statuses/set-to-ready-to-ship",
                # json_data=payload.model_dump(by_alias=True, exclude_none=True)
            )
        else:
            raise ValueError(f"Status transition to {status} not implemented in set_status_async method")

    def set_status_delivered(self, order_item_ids: List[int]) -> Dict[str, List[int]]:
        """Set orders items statuses to delivered.
        
        Items (and orders) must be in 'shipped' or 'delivered' status. For 'digital' 
        items this transition is also allowed from status 'pending'.
        """
        json_data = {"orderItemIds": order_item_ids}
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/orders/statuses/set-to-delivered", 
            json_data=json_data
        )
        return response_data
    
    async def set_status_delivered_async(self, order_item_ids: List[int]) -> Dict[str, List[int]]:
        """Set orders items statuses to delivered (async)."""
        json_data = {"orderItemIds": order_item_ids}
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/orders/statuses/set-to-delivered", 
            json_data=json_data
        )
        return response_data
    
    def set_status_shipped(self, order_item_ids: List[int]) -> Dict[str, List[int]]:
        """Set orders items statuses to shipped.
        
        All order items must belong to same order. Items (and orders) must be in 'ready to ship' status.
        """
        json_data = {"orderItemIds": order_item_ids}
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/orders/statuses/set-to-shipped", 
            json_data=json_data
        )
        return response_data
    
    async def set_status_shipped_async(self, order_item_ids: List[int]) -> Dict[str, List[int]]:
        """Set orders items statuses to shipped (async)."""
        json_data = {"orderItemIds": order_item_ids}
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/orders/statuses/set-to-shipped", 
            json_data=json_data
        )
        return response_data
    
    def set_status_return_received(self, order_item_ids: List[int]) -> Dict[str, List[int]]:
        """Set orders items statuses to return received.
        
        Items (and orders) must be in 'Return Shipped By Customer' status.
        """
        json_data = {"orderItemIds": order_item_ids}
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/orders/statuses/set-to-return-received", 
            json_data=json_data
        )
        return response_data
    
    async def set_status_return_received_async(self, order_item_ids: List[int]) -> Dict[str, List[int]]:
        """Set orders items statuses to return received (async)."""
        json_data = {"orderItemIds": order_item_ids}
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/orders/statuses/set-to-return-received", 
            json_data=json_data
        )
        return response_data
    
    def set_status_return_approved(self, order_item_ids: List[int]) -> Dict[str, List[int]]:
        """Set orders items statuses to return approved.
        
        To approve order items they must meet the following conditions:
        1. Items and Order must be in 'Return Waiting For Approval' status
        2. Setting 'Manage Returns' must be set as 'Seller can receive returned items from warehouse'
        """
        json_data = {"orderItemIds": order_item_ids}
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/orders/statuses/set-to-return-approved", 
            json_data=json_data
        )
        return response_data
    
    async def set_status_return_approved_async(self, order_item_ids: List[int]) -> Dict[str, List[int]]:
        """Set orders items statuses to return approved (async)."""
        json_data = {"orderItemIds": order_item_ids}
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/orders/statuses/set-to-return-approved", 
            json_data=json_data
        )
        return response_data
    
    def set_status_cancelled(self, order_item_ids: List[int], reason: str, reason_detail: Optional[str] = None) -> Dict[str, List[int]]:
        """Set orders items statuses to cancelled.
        
        Only orders items on statuses 'pending' or 'ready to ship' can be cancelled.
        Digital items cancellation is possible only for 'pending' status.
        """
        json_data = {
            "orderItemIds": order_item_ids,
            "reason": reason
        }
        if reason_detail:
            json_data["reasonDetail"] = reason_detail
            
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/orders/statuses/set-to-cancelled", 
            json_data=json_data
        )
        return response_data
    
    async def set_status_cancelled_async(self, order_item_ids: List[int], reason: str, reason_detail: Optional[str] = None) -> Dict[str, List[int]]:
        """Set orders items statuses to cancelled (async)."""
        json_data = {
            "orderItemIds": order_item_ids,
            "reason": reason
        }
        if reason_detail:
            json_data["reasonDetail"] = reason_detail
            
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/orders/statuses/set-to-cancelled", 
            json_data=json_data
        )
        return response_data
    
    def set_status_ready_to_ship(
        self, 
        order_items: List[Dict[str, Any]], 
        tracking_number: str,
        delivery_type: Literal["dropship", "pickup", "send_to_warehouse"],
        shipping_provider: Optional[str] = None,
        access_key: Optional[str] = None,
        document_url: Optional[str] = None,
        invoice_encoded_xml: Optional[str] = None
    ) -> Dict[str, List[int]]:
        """Set orders items statuses to ready to ship.
        
        Order items must be from the same order and all must have status 'pending'.
        """
        json_data = {
            "orderItems": order_items,
            "trackingNumber": tracking_number,
            "deliveryType": delivery_type
        }
        
        if shipping_provider:
            json_data["shippingProvider"] = shipping_provider
        if access_key:
            json_data["accessKey"] = access_key
        if document_url:
            json_data["documentUrl"] = document_url
        if invoice_encoded_xml:
            json_data["invoiceEncodedXml"] = invoice_encoded_xml
        
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/orders/statuses/set-to-ready-to-ship", 
            json_data=json_data
        )
        return response_data
    
    async def set_status_ready_to_ship_async(
        self, 
        order_items: List[Dict[str, Any]], 
        tracking_number: str,
        delivery_type: Literal["dropship", "pickup", "send_to_warehouse"],
        shipping_provider: Optional[str] = None,
        access_key: Optional[str] = None,
        document_url: Optional[str] = None,
        invoice_encoded_xml: Optional[str] = None
    ) -> Dict[str, List[int]]:
        """Set orders items statuses to ready to ship (async)."""
        json_data = {
            "orderItems": order_items,
            "trackingNumber": tracking_number,
            "deliveryType": delivery_type
        }
        
        if shipping_provider:
            json_data["shippingProvider"] = shipping_provider
        if access_key:
            json_data["accessKey"] = access_key
        if document_url:
            json_data["documentUrl"] = document_url
        if invoice_encoded_xml:
            json_data["invoiceEncodedXml"] = invoice_encoded_xml
        
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/orders/statuses/set-to-ready-to-ship", 
            json_data=json_data
        )
        return response_data
    
    def set_status_packed_by_marketplace(
        self,
        order_items: List[Dict[str, Any]],
        delivery_type: Literal["dropship", "pickup", "send_to_warehouse"],
        shipping_provider: Optional[str] = None,
        tracking_number: Optional[str] = None
    ) -> Dict[str, List[int]]:
        """Set orders items statuses to packed by marketplace.
        
        Only orders items on status 'pending' can be packed by marketplace.
        """
        json_data = {
            "orderItems": order_items,
            "deliveryType": delivery_type
        }
        
        if shipping_provider:
            json_data["shippingProvider"] = shipping_provider
        if tracking_number:
            json_data["trackingNumber"] = tracking_number
        
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/orders/statuses/set-to-packed-by-marketplace", 
            json_data=json_data
        )
        return response_data
    
    async def set_status_packed_by_marketplace_async(
        self,
        order_items: List[Dict[str, Any]],
        delivery_type: Literal["dropship", "pickup", "send_to_warehouse"],
        shipping_provider: Optional[str] = None,
        tracking_number: Optional[str] = None
    ) -> Dict[str, List[int]]:
        """Set orders items statuses to packed by marketplace (async)."""
        json_data = {
            "orderItems": order_items,
            "deliveryType": delivery_type
        }
        
        if shipping_provider:
            json_data["shippingProvider"] = shipping_provider
        if tracking_number:
            json_data["trackingNumber"] = tracking_number
        
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/orders/statuses/set-to-packed-by-marketplace", 
            json_data=json_data
        )
        return response_data
    
    def set_status_return_rejected(
        self,
        order_item_ids: List[int],
        reason: str,
        reason_detail: Optional[str] = None
    ) -> Dict[str, List[int]]:
        """Set orders items statuses to return rejected.
        
        To reject order items they must meet following conditions:
        1. Order Items must be in 'waiting for approval' status
        2. Setting 'Manage Returns' must be set as 'Seller can receive returned items from customer'
        """
        json_data = {
            "orderItemIds": order_item_ids,
            "reason": reason
        }
        if reason_detail:
            json_data["reasonDetail"] = reason_detail
            
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/orders/statuses/set-to-return-rejected", 
            json_data=json_data
        )
        return response_data
    
    async def set_status_return_rejected_async(
        self,
        order_item_ids: List[int],
        reason: str,
        reason_detail: Optional[str] = None
    ) -> Dict[str, List[int]]:
        """Set orders items statuses to return rejected (async)."""
        json_data = {
            "orderItemIds": order_item_ids,
            "reason": reason
        }
        if reason_detail:
            json_data["reasonDetail"] = reason_detail
            
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/orders/statuses/set-to-return-rejected", 
            json_data=json_data
        )
        return response_data
    
    def set_status_returned(
        self,
        order_item_ids: List[int],
        reason: Optional[str] = None
    ) -> Dict[str, List[int]]:
        """Set orders items statuses to returned.
        
        Order items must be in 'delivered' status.
        """
        json_data = {"orderItemIds": order_item_ids}
        if reason:
            json_data["reason"] = reason
            
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/orders/statuses/set-to-returned", 
            json_data=json_data
        )
        return response_data
    
    async def set_status_returned_async(
        self,
        order_item_ids: List[int],
        reason: Optional[str] = None
    ) -> Dict[str, List[int]]:
        """Set orders items statuses to returned (async)."""
        json_data = {"orderItemIds": order_item_ids}
        if reason:
            json_data["reason"] = reason
            
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/orders/statuses/set-to-returned", 
            json_data=json_data
        )
        return response_data
    
    def set_status_delivery_failed(
        self,
        order_item_ids: List[int],
        reason: str,
        reason_detail: Optional[str] = None
    ) -> Dict[str, List[int]]:
        """Set orders items statuses to delivery failed.
        
        Order items must be in 'shipped' status.
        """
        json_data = {
            "orderItemIds": order_item_ids,
            "reason": reason
        }
        if reason_detail:
            json_data["reasonDetail"] = reason_detail
            
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/orders/statuses/set-to-delivery-failed", 
            json_data=json_data
        )
        return response_data
    
    async def set_status_delivery_failed_async(
        self,
        order_item_ids: List[int],
        reason: str,
        reason_detail: Optional[str] = None
    ) -> Dict[str, List[int]]:
        """Set orders items statuses to delivery failed (async)."""
        json_data = {
            "orderItemIds": order_item_ids,
            "reason": reason
        }
        if reason_detail:
            json_data["reasonDetail"] = reason_detail
            
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/orders/statuses/set-to-delivery-failed", 
            json_data=json_data
        )
        return response_data

    def upload_document_for_package(
        self, package_id: int, document_type: str, document_file_path: str
    ) -> Dict[str, int]:
        """Upload sales order document for a package."""
        with open(document_file_path, "rb") as f:
            files = {"documentFile": (document_file_path.split('/')[-1], f)}
            form_data = {"documentType": document_type}
            # Note: httpx typically sets Content-Type for files/data correctly.
            # For multipart/form-data, pass `files` and `data` (not `json_data`).
            response_data = self._client._make_request_sync( # type: ignore
                "POST",
                f"/v2/order/document/package/{package_id}",
                form_data=form_data, # For form fields
                files=files         # For file part
            )
        return response_data # Example: {"id": 672}