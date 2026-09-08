from typing import Dict, Any, List, Literal, Optional, Union, TYPE_CHECKING
from datetime import datetime, timezone

from .base import IconicResource
from ..models import (
    ProductRead,
    PriceRead,
    RejectedProductSet
)

from ..models.stock import StockData, StockUpdateItem

if TYPE_CHECKING:
    from .product_set import ProductSet
    from ..models.stock import StockData, StockUpdateItem

#: ``GET /v2/product/seller-skus`` refuses more than 100 SKUs in one call.
MAX_SELLER_SKUS_PER_REQUEST = 100

#: The only fields ``PUT /v2/product-set/{productSetId}/products/{productId}`` will act on.
#: Everything else in the schema is ``readOnly`` and is silently discarded by the API,
#: so sending it produces a successful-looking no-op.
PRODUCT_WRITABLE_FIELDS = frozenset({
    "sellerSku",
    "status",
    "variation",
    "shipmentTypeId",
    "productIdentifier",
    "name",
})


def _format_datetime(value: Union[datetime, str]) -> str:
    """
    Render a sale date the way the price endpoints expect it.

    The spec types ``saleStartDate`` / ``saleEndDate`` as ``string(date-time)``.
    A naive datetime is assumed to be UTC and gets a ``Z`` suffix; an aware one is
    converted to UTC first. Blindly appending ``"Z"`` to ``isoformat()`` -- which is
    what this module used to do -- yields ``...+00:00Z`` for an aware datetime, which
    is not a valid timestamp.

    Args:
        value: A datetime, or an already-formatted string which is passed through

    Returns:
        An ISO-8601 UTC timestamp such as ``2025-01-31T00:00:00Z``
    """
    if isinstance(value, str):
        return value
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.isoformat() + "Z"


class Product(IconicResource):
    """
    Product resource representing a single product or a collection of products.
    
    When initialized with data, it represents a specific product.
    Otherwise, it represents the collection of all products.
    """
    
    endpoint = "product"
    model_class = ProductRead
    
    def list(self, paginated: bool = False, **params) -> List["Product"]:
        return super().list(paginated=paginated, pluralised=True, **params)

    def get(self, resource_id: Any, pluralised: bool = False) -> "Product":
        """
        Get a single product by its numeric product id.

        ``GET /v2/product/{productId}`` -- which the inherited ``IconicResource.get``
        would build from ``endpoint = "product"`` -- **does not exist** in the API. The
        supported ways to read one variation are ``GET /v2/products?productIds[]={id}``
        (used here), ``GET /v2/product-set/{productSetId}/products/{productId}``, or the
        seller-sku / shop-sku lookups.

        Args:
            resource_id: The numeric product id
            pluralised: Accepted for signature compatibility with the base class; ignored

        Returns:
            The Product resource

        Raises:
            ValueError: If no product with that id belongs to this seller
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")

        url = "/v2/products"
        params = {"productIds[]": [int(resource_id)]}

        response = self._client._make_request_sync("GET", url, params=params)
        items = self._extract_items(response)

        if not items:
            raise ValueError(f"No product found with id {resource_id}")

        return Product(client=self._client, data=items[0])

    async def get_async(self, resource_id: Any, pluralised: bool = False) -> "Product":
        """
        Get a single product by its numeric product id asynchronously.

        See ``get`` -- ``GET /v2/product/{productId}`` does not exist, so this goes
        through ``GET /v2/products?productIds[]={id}``.

        Args:
            resource_id: The numeric product id
            pluralised: Accepted for signature compatibility with the base class; ignored

        Returns:
            The Product resource

        Raises:
            ValueError: If no product with that id belongs to this seller
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")

        url = "/v2/products"
        params = {"productIds[]": [int(resource_id)]}

        response = await self._client._make_request_async("GET", url, params=params)
        items = self._extract_items(response)

        if not items:
            raise ValueError(f"No product found with id {resource_id}")

        return Product(client=self._client, data=items[0])

    def get_by_shop_sku(self, shop_sku: str) -> "Product":
        """Get a product by its shop SKU."""
        url = f"/v2/product/shop-sku/{shop_sku}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_by_shop_sku_async(self, shop_sku: str) -> "Product":
        """Get a product by its shop SKU asynchronously."""
        url = f"/v2/product/shop-sku/{shop_sku}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_by_seller_sku(self, seller_sku: str) -> "Product":
        """Get a product by its seller SKU."""
        url = f"/v2/product/seller-sku/{seller_sku}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_by_seller_sku_async(self, seller_sku: str) -> "Product":
        """Get a product by its seller SKU asynchronously."""
        url = f"/v2/product/seller-sku/{seller_sku}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def list_by_seller_skus(self, seller_skus: List[str], limit: int = 100, offset: int = 0) -> List["Product"]:
        """
        Get products by multiple seller SKUs.

        ``limit`` and ``offset`` are REQUIRED query parameters on this endpoint, and no
        more than 100 SKUs may be searched at once.
        """
        if len(seller_skus) > MAX_SELLER_SKUS_PER_REQUEST:
            raise ValueError(
                f"Cannot look up more than {MAX_SELLER_SKUS_PER_REQUEST} seller SKUs "
                f"in a single request, got {len(seller_skus)}"
            )

        url = "/v2/product/seller-skus"
        params = {
            "sellerSkus[]": seller_skus,
            "limit": limit,
            "offset": offset
        }
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            
            if isinstance(response, dict) and "items" in response:
                items = response.get("items", [])
            else:
                items = response
                
            return [Product(client=self._client, data=item) for item in items]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_by_seller_skus_async(self, seller_skus: List[str], limit: int = 100, offset: int = 0) -> List["Product"]:
        """
        Get products by multiple seller SKUs asynchronously.

        ``limit`` and ``offset`` are REQUIRED query parameters on this endpoint, and no
        more than 100 SKUs may be searched at once.
        """
        if len(seller_skus) > MAX_SELLER_SKUS_PER_REQUEST:
            raise ValueError(
                f"Cannot look up more than {MAX_SELLER_SKUS_PER_REQUEST} seller SKUs "
                f"in a single request, got {len(seller_skus)}"
            )

        url = "/v2/product/seller-skus"
        params = {
            "sellerSkus[]": seller_skus,
            "limit": limit,
            "offset": offset
        }
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            
            if isinstance(response, dict) and "items" in response:
                items = response.get("items", [])
            else:
                items = response
                
            return [Product(client=self._client, data=item) for item in items]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Price related methods
    
    def _build_price_payload(
        self,
        price: Optional[float],
        sale_price: Optional[float],
        sale_start_date: Optional[Union[datetime, str]],
        sale_end_date: Optional[Union[datetime, str]],
        status: Optional[str],
    ) -> Dict[str, Any]:
        """Build the body of ``PUT /v2/product/{productId}/prices/{country}``."""
        payload: Dict[str, Any] = {}

        if price is not None:
            payload["price"] = price
        if sale_price is not None:
            payload["salePrice"] = sale_price
        if sale_start_date is not None:
            payload["saleStartDate"] = _format_datetime(sale_start_date)
        if sale_end_date is not None:
            payload["saleEndDate"] = _format_datetime(sale_end_date)
        if status:
            payload["status"] = status

        return payload

    def update_price(self,
                   country: str,
                   price: Optional[float] = None,
                   sale_price: Optional[float] = None,
                   sale_start_date: Optional[Union[datetime, str]] = None,
                   sale_end_date: Optional[Union[datetime, str]] = None,
                   status: Optional[Literal["active", "inactive"]] = "active") -> PriceRead:
        """
        Update the price of this product for a given country.

        ``PUT /v2/product/{productId}/prices/{country}``. The country is a PATH
        parameter (an ISO 3166-1 alpha-2 code such as ``"AU"``; the enabled list comes
        from ``GET /v2/countries/enabled``). There is **no currency field anywhere in
        the price schemas** -- the country alone selects the currency.

        .. warning::
           Omission is not "leave alone". The spec: "No values are required here however
           if you leave them empty they all will be updated with null/empty values. The
           only difference is ``status`` which remains the same as it was originally."
           So calling this with only ``price=`` WIPES an active sale price and its dates.
           Always pass the complete price state you want the row to end up in.

        Args:
            country: ISO 3166-1 alpha-2 country code, e.g. "AU"
            price: Regular price. Omitting it nulls the stored price.
            sale_price: Sale price; must be lower than ``price``. Omitting it clears the sale.
            sale_start_date: Sale start; must be after 2010-01-01
            sale_end_date: Sale end; must be in the future, after ``sale_start_date``,
                           and no more than 100 years out
            status: 'active' or 'inactive' -- whether the product may be sold in this
                    country. This is the one field that survives being omitted.

        Returns:
            The price row as the API stored it
        """
        if not self.id:
            raise ValueError("Cannot update price without a product ID")

        url = f"/v2/product/{self.id}/prices/{country}"
        payload = self._build_price_payload(price, sale_price, sale_start_date, sale_end_date, status)

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("PUT", url, json_data=payload)
            return PriceRead(**response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def update_price_async(self,
                              country: str,
                              price: Optional[float] = None,
                              sale_price: Optional[float] = None,
                              sale_start_date: Optional[Union[datetime, str]] = None,
                              sale_end_date: Optional[Union[datetime, str]] = None,
                              status: Optional[Literal["active", "inactive"]] = "active") -> PriceRead:
        """
        Update the price of this product for a given country asynchronously.

        See ``update_price`` -- in particular the warning that every price field you
        omit is written as NULL, and that the price endpoints have no currency field.

        Args:
            country: ISO 3166-1 alpha-2 country code, e.g. "AU"
            price: Regular price. Omitting it nulls the stored price.
            sale_price: Sale price; must be lower than ``price``
            sale_start_date: Sale start; must be after 2010-01-01
            sale_end_date: Sale end; must be in the future and after ``sale_start_date``
            status: 'active' or 'inactive'; the only field that survives omission

        Returns:
            The price row as the API stored it
        """
        if not self.id:
            raise ValueError("Cannot update price without a product ID")

        url = f"/v2/product/{self.id}/prices/{country}"
        payload = self._build_price_payload(price, sale_price, sale_start_date, sale_end_date, status)

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("PUT", url, json_data=payload)
            return PriceRead(**response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def update_price_status(self, country: str, status: Literal["active", "inactive"]) -> None:
        """
        Update the price status of this product for a given country.

        ``PUT /v2/product/{productId}/prices/{country}/status`` with a JSON body of
        ``{"status": ...}``. Unlike the product-level status endpoint this one really
        does take a body. It answers 204 No Content, so there is nothing to parse, and
        it leaves every other value of the price row untouched -- which makes it the
        safe way to activate/deactivate a country without re-sending the whole price.

        Args:
            country: ISO 3166-1 alpha-2 country code, e.g. "AU"
            status: 'active' or 'inactive'
        """
        if not self.id:
            raise ValueError("Cannot update price status without a product ID")

        url = f"/v2/product/{self.id}/prices/{country}/status"
        payload = {"status": status}

        if hasattr(self._client, '_make_request_sync'):
            self._client._make_request_sync("PUT", url, json_data=payload)
        else:
            raise TypeError("This method requires a synchronous client")

    async def update_price_status_async(self, country: str, status: Literal["active", "inactive"]) -> None:
        """
        Update the price status of this product for a given country asynchronously.

        ``PUT /v2/product/{productId}/prices/{country}/status``; body ``{"status": ...}``,
        204 No Content, other price values untouched.

        Args:
            country: ISO 3166-1 alpha-2 country code, e.g. "AU"
            status: 'active' or 'inactive'
        """
        if not self.id:
            raise ValueError("Cannot update price status without a product ID")

        url = f"/v2/product/{self.id}/prices/{country}/status"
        payload = {"status": status}

        if hasattr(self._client, '_make_request_async'):
            await self._client._make_request_async("PUT", url, json_data=payload)
        else:
            raise TypeError("This method requires an asynchronous client")
    
    # Product set related methods
    
    @property
    def product_set_id(self) -> Optional[int]:
        """Get the product set ID that this product belongs to."""
        return self._data.get("productSetId")
    
    def get_product_set(self) -> "ProductSet":
        """Get the product set that this product belongs to."""
        if not self.product_set_id:
            raise ValueError("This product does not have a product set ID")
            
        from .product_set import ProductSet
        
        if hasattr(self._client, '_make_request_sync'):
            url = f"/v2/product-set/{self.product_set_id}"
            response = self._client._make_request_sync("GET", url)
            return ProductSet(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_product_set_async(self) -> "ProductSet":
        """Get the product set that this product belongs to asynchronously."""
        if not self.product_set_id:
            raise ValueError("This product does not have a product set ID")
            
        from .product_set import ProductSet
        
        if hasattr(self._client, '_make_request_async'):
            url = f"/v2/product-set/{self.product_set_id}"
            response = await self._client._make_request_async("GET", url)
            return ProductSet(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Status related methods
    
    def update_status(self, status: Literal["active", "inactive", "deleted"]) -> "Product":
        """
        Update the status of this product (variation).

        ``PUT /v2/product-set/{productSetId}/products/{productId}/status`` takes
        ``status`` as a QUERY parameter and has **no request body at all**; it answers
        200 with no content. Sending the status in a JSON body instead is accepted by
        the server and does nothing.

        This is also the endpoint that undeletes a product -- ``PUT /v2/product-set/{id}``
        errors outright while every variation in the set is deleted.

        Args:
            status: 'active', 'inactive' or 'deleted'

        Returns:
            This Product, with its local status updated
        """
        if not self.id or not self.product_set_id:
            raise ValueError("Cannot update status without a product ID and product set ID")

        url = f"/v2/product-set/{self.product_set_id}/products/{self.id}/status"
        params = {"status": status}

        if hasattr(self._client, '_make_request_sync'):
            self._client._make_request_sync("PUT", url, params=params)
            # Update the local status
            self._data["status"] = status
            if self._model:
                setattr(self._model, "status", status)
            return self
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def update_status_async(self, status: Literal["active", "inactive", "deleted"]) -> "Product":
        """
        Update the status of this product (variation) asynchronously.

        ``status`` is a QUERY parameter on this endpoint and there is no request body;
        see ``update_status``.

        Args:
            status: 'active', 'inactive' or 'deleted'

        Returns:
            This Product, with its local status updated
        """
        if not self.id or not self.product_set_id:
            raise ValueError("Cannot update status without a product ID and product set ID")

        url = f"/v2/product-set/{self.product_set_id}/products/{self.id}/status"
        params = {"status": status}

        if hasattr(self._client, '_make_request_async'):
            await self._client._make_request_async("PUT", url, params=params)
            # Update the local status
            self._data["status"] = status
            if self._model:
                setattr(self._model, "status", status)
            return self
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def _prepare_product_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Camel-case and validate a body for ``PUT /v2/product-set/{id}/products/{productId}``.

        The endpoint acts on ``sellerSku``, ``status``, ``variation``, ``shipmentTypeId``,
        ``productIdentifier`` and ``name`` only -- "Other attributes will be discarded" --
        and a delete/undelete makes it ignore every other field in the same request. Both
        rules fail silently server-side, so they are enforced here instead.
        """
        prepared_data = self._prepare_request_data(data)

        unsupported = sorted(set(prepared_data) - PRODUCT_WRITABLE_FIELDS)
        if unsupported:
            raise ValueError(
                f"PUT /v2/product-set/{{id}}/products/{{productId}} discards these fields: "
                f"{', '.join(unsupported)}. Writable fields are: "
                f"{', '.join(sorted(PRODUCT_WRITABLE_FIELDS))}."
            )

        new_status = prepared_data.get("status")
        current_status = self._data.get("status")
        is_delete_or_undelete = new_status == "deleted" or (
            current_status == "deleted" and new_status is not None and new_status != "deleted"
        )
        if is_delete_or_undelete and len(prepared_data) > 1:
            raise ValueError(
                "Deleting or undeleting a product makes the API ignore every other field "
                "in the same request. Send the status change on its own, then re-apply "
                f"the remaining fields: {', '.join(sorted(set(prepared_data) - {'status'}))}."
            )

        return prepared_data

    def update(self, data: Dict[str, Any]) -> "Product":
        """
        Update this product (variation).

        ``PUT /v2/product-set/{productSetId}/products/{productId}``. Only ``sellerSku``,
        ``status``, ``variation``, ``shipmentTypeId``, ``productIdentifier`` and ``name``
        can be written; anything else raises rather than being silently discarded by the
        API. Price is NOT a product field -- use ``update_price``.

        Args:
            data: The fields to change, snake_case or camelCase

        Returns:
            This Product, refreshed from the response
        """
        if not self.id or not self.product_set_id:
            raise ValueError("Cannot update without a product ID and product set ID")

        url = f"/v2/product-set/{self.product_set_id}/products/{self.id}"
        prepared_data = self._prepare_product_update(data)

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
            # Update this instance's data
            self._data.update(response)
            if self.model_class:
                self._model = self.model_class(**self._data)
            return self
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def update_async(self, data: Dict[str, Any]) -> "Product":
        """
        Update this product (variation) asynchronously.

        Only ``sellerSku``, ``status``, ``variation``, ``shipmentTypeId``,
        ``productIdentifier`` and ``name`` are writable; see ``update``.

        Args:
            data: The fields to change, snake_case or camelCase

        Returns:
            This Product, refreshed from the response
        """
        if not self.id or not self.product_set_id:
            raise ValueError("Cannot update without a product ID and product set ID")

        url = f"/v2/product-set/{self.product_set_id}/products/{self.id}"
        prepared_data = self._prepare_product_update(data)

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
            # Update this instance's data
            self._data.update(response)
            if self.model_class:
                self._model = self.model_class(**self._data)
            return self
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Stock related methods
    
    def get_stock(self) -> "StockData":
        """
        Get stock information for this product.

        ``GET /v2/stock/product/{productId}`` -- ``quantity`` is the sellable stock in
        the seller's own warehouse, ``available`` the computed total.

        Returns:
            StockData object containing product stock information
        """
        if not self.id:
            raise ValueError("Cannot get stock without a product ID")

        if hasattr(self._client, 'stock'):
            return self._client.stock.get_product_stock(self.id)
        else:
            raise ValueError("Client does not have a stock resource")

    async def get_stock_async(self) -> "StockData":
        """
        Get stock information for this product asynchronously.

        Returns:
            StockData object containing product stock information
        """
        if not self.id:
            raise ValueError("Cannot get stock without a product ID")

        if hasattr(self._client, 'stock'):
            return await self._client.stock.get_product_stock_async(self.id)
        else:
            raise ValueError("Client does not have a stock resource")

    def update_stock(self, quantity: int) -> bool:
        """
        Update the stock quantity for this product.

        ``PUT /v2/stock/product`` answers with the items it REFUSED to update, so the
        response is checked for this product rather than returned as a confirmation.
        (Before 0.2.0 this method returned ``result[0]`` -- the failure row -- as if it
        were proof the write had landed, which inverted the meaning of the call.)

        Args:
            quantity: The new stock quantity

        Returns:
            True if the API accepted the update, False if it ignored this product
            (products fulfilled by the venture can never be updated this way)
        """
        if not self.id:
            raise ValueError("Cannot update stock without a product ID")

        if hasattr(self._client, 'stock'):
            failed = self._client.stock.update_stock([
                {"productId": self.id, "quantity": quantity}
            ])
            return not failed
        else:
            raise ValueError("Client does not have a stock resource")

    async def update_stock_async(self, quantity: int) -> bool:
        """
        Update the stock quantity for this product asynchronously.

        The endpoint answers with the items it REFUSED to update; see ``update_stock``.

        Args:
            quantity: The new stock quantity

        Returns:
            True if the API accepted the update, False if it ignored this product
        """
        if not self.id:
            raise ValueError("Cannot update stock without a product ID")

        if hasattr(self._client, 'stock'):
            failed = await self._client.stock.update_stock_async([
                {"productId": self.id, "quantity": quantity}
            ])
            return not failed
        else:
            raise ValueError("Client does not have a stock resource")
    
    # Quality control related methods
    
    @classmethod
    def get_rejected_product_sets(cls, client: Any, product_set_ids: List[int]) -> List[RejectedProductSet]:
        """Get information about rejected product sets."""
        url = "/v2/product-quality-control/rejected"
        params = {"productSetIds[]": product_set_ids}
        
        if hasattr(client, '_make_request_sync'):
            response = client._make_request_sync("GET", url, params=params)
            return [RejectedProductSet(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    @classmethod
    async def get_rejected_product_sets_async(cls, client: Any, product_set_ids: List[int]) -> List[RejectedProductSet]:
        """Get information about rejected product sets asynchronously."""
        url = "/v2/product-quality-control/rejected"
        params = {"productSetIds[]": product_set_ids}
        
        if hasattr(client, '_make_request_async'):
            response = await client._make_request_async("GET", url, params=params)
            return [RejectedProductSet(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
