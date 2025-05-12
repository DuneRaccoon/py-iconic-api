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
            
        response_data = self._client._make_request_sync( # type: ignore
            "POST",
            "/v2/orders/statuses/set-to-ready-to-ship",
            # json_data=payload.model_dump(by_alias=True, exclude_none=True)
        )
        return response_data # Example: {"orderItemIds": [123, 456]}

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