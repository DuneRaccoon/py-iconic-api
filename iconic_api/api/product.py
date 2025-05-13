from typing import Optional, List, Dict, Any, Union, TypeVar, Generic
from datetime import datetime
from .base_api_module import BaseAPIModule
from ..models import (
    Product,
    ProductRead,
    PriceRead,
    RejectedProductSet
)

T = TypeVar('T')

class PaginatedResponse(Generic[T]):
    """Generic class for paginated responses."""
    def __init__(self, items: List[T], limit: int, offset: int, total_count: int):
        self.items = items
        self.limit = limit
        self.offset = offset
        self.total_count = total_count

class ProductAPI(BaseAPIModule):
    def get_product_by_shop_sku(self, shop_sku: str) -> ProductRead:
        """
        Get a product by shop SKU.
        
        Args:
            shop_sku: Shop SKU of the product
            
        Returns:
            The requested product
        """
        response_data = self._client._make_request_sync(
            "GET", 
            f"/v2/product/shop-sku/{shop_sku}"
        )
        
        return ProductRead(**response_data)
    
    async def get_product_by_shop_sku_async(self, shop_sku: str) -> ProductRead:
        """
        Get a product by shop SKU (async).
        
        Args:
            shop_sku: Shop SKU of the product
            
        Returns:
            The requested product
        """
        response_data = await self._client._make_request_async(
            "GET", 
            f"/v2/product/shop-sku/{shop_sku}"
        )
        
        return ProductRead(**response_data)
    
    def get_product_by_seller_sku(self, seller_sku: str) -> ProductRead:
        """
        Get a product by seller SKU.
        
        Args:
            seller_sku: Seller SKU of the product
            
        Returns:
            The requested product
        """
        response_data = self._client._make_request_sync(
            "GET", 
            f"/v2/product/seller-sku/{seller_sku}"
        )
        
        return ProductRead(**response_data)
    
    async def get_product_by_seller_sku_async(self, seller_sku: str) -> ProductRead:
        """
        Get a product by seller SKU (async).
        
        Args:
            seller_sku: Seller SKU of the product
            
        Returns:
            The requested product
        """
        response_data = await self._client._make_request_async(
            "GET", 
            f"/v2/product/seller-sku/{seller_sku}"
        )
        
        return ProductRead(**response_data)
    
    def get_products_by_seller_skus(self, seller_skus: List[str], limit: int = 100, offset: int = 0) -> PaginatedResponse[ProductRead]:
        """
        Get products by multiple seller SKUs.
        
        Args:
            seller_skus: List of seller SKUs (max 100)
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            Paginated response containing products matching the seller SKUs
        """
        params = {
            "sellerSkus[]": seller_skus,
            "limit": limit,
            "offset": offset
        }
        
        response_data = self._client._make_request_sync(
            "GET", 
            "/v2/product/seller-skus", 
            params=params
        )
        
        # Extract pagination data and create items list
        items = [ProductRead(**item) for item in response_data.get("items", [])]
        pagination = response_data.get("pagination", {})
        limit = pagination.get("limit", limit)
        offset = pagination.get("offset", offset)
        total_count = pagination.get("totalCount", len(items))
        
        return PaginatedResponse(items, limit, offset, total_count)
    
    async def get_products_by_seller_skus_async(self, seller_skus: List[str], limit: int = 100, offset: int = 0) -> PaginatedResponse[ProductRead]:
        """
        Get products by multiple seller SKUs (async).
        
        Args:
            seller_skus: List of seller SKUs (max 100)
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            Paginated response containing products matching the seller SKUs
        """
        params = {
            "sellerSkus[]": seller_skus,
            "limit": limit,
            "offset": offset
        }
        
        response_data = await self._client._make_request_async(
            "GET", 
            "/v2/product/seller-skus", 
            params=params
        )
        
        # Extract pagination data and create items list
        items = [ProductRead(**item) for item in response_data.get("items", [])]
        pagination = response_data.get("pagination", {})
        limit = pagination.get("limit", limit)
        offset = pagination.get("offset", offset)
        total_count = pagination.get("totalCount", len(items))
        
        return PaginatedResponse(items, limit, offset, total_count)
    
    def list_products(self, 
                     product_uuids: Optional[List[str]] = None,
                     product_ids: Optional[List[int]] = None,
                     seller_id: Optional[int] = None,
                     sku: Optional[str] = None,
                     name: Optional[str] = None,
                     seller_sku: Optional[str] = None) -> List[ProductRead]:
        """
        Get list of products with filters.
        
        Args:
            product_uuids: List of product UUIDs
            product_ids: List of product IDs
            seller_id: Seller ID
            sku: Product SKU
            name: Product name
            seller_sku: Seller SKU
            
        Returns:
            List of products matching the filters
        """
        params = {}
        if product_uuids:
            params["productUuids[]"] = product_uuids
        if product_ids:
            params["productIds[]"] = product_ids
        if seller_id:
            params["sellerId"] = seller_id
        if sku:
            params["sku"] = sku
        if name:
            params["name"] = name
        if seller_sku:
            params["sellerSku"] = seller_sku
        
        response_data = self._client._make_request_sync(
            "GET", 
            "/v2/products", 
            params=params
        )
        
        return [ProductRead(**item) for item in response_data]
    
    async def list_products_async(self, 
                                product_uuids: Optional[List[str]] = None,
                                product_ids: Optional[List[int]] = None,
                                seller_id: Optional[int] = None,
                                sku: Optional[str] = None,
                                name: Optional[str] = None,
                                seller_sku: Optional[str] = None) -> List[ProductRead]:
        """
        Get list of products with filters (async).
        
        Args:
            product_uuids: List of product UUIDs
            product_ids: List of product IDs
            seller_id: Seller ID
            sku: Product SKU
            name: Product name
            seller_sku: Seller SKU
            
        Returns:
            List of products matching the filters
        """
        params = {}
        if product_uuids:
            params["productUuids[]"] = product_uuids
        if product_ids:
            params["productIds[]"] = product_ids
        if seller_id:
            params["sellerId"] = seller_id
        if sku:
            params["sku"] = sku
        if name:
            params["name"] = name
        if seller_sku:
            params["sellerSku"] = seller_sku
        
        response_data = await self._client._make_request_async(
            "GET", 
            "/v2/products", 
            params=params
        )
        
        return [ProductRead(**item) for item in response_data]
    
    # New methods for updating product prices
    
    def update_product_price(self, 
                           product_id: int, 
                           country: str,
                           price: Optional[float] = None,
                           sale_price: Optional[float] = None,
                           sale_start_date: Optional[datetime] = None,
                           sale_end_date: Optional[datetime] = None,
                           status: str = "active") -> PriceRead:
        """
        Update Product Price for a given country.
        
        Args:
            product_id: Numeric ID of the Product
            country: Country code
            price: Price of the product
            sale_price: Sale price of the product
            sale_start_date: Start date of a sale pricing
            sale_end_date: End date of a sale pricing
            status: Price status (active/inactive)
            
        Returns:
            The updated price information
        """
        payload = {}
        if price is not None:
            payload["price"] = price
        if sale_price is not None:
            payload["salePrice"] = sale_price
        if sale_start_date is not None:
            payload["saleStartDate"] = sale_start_date.isoformat() + "Z"
        if sale_end_date is not None:
            payload["saleEndDate"] = sale_end_date.isoformat() + "Z"
        if status:
            payload["status"] = status
        
        response_data = self._client._make_request_sync(
            "PUT", 
            f"/v2/product/{product_id}/prices/{country}", 
            json_data=payload
        )
        
        return PriceRead(**response_data)
    
    async def update_product_price_async(self, 
                                      product_id: int, 
                                      country: str,
                                      price: Optional[float] = None,
                                      sale_price: Optional[float] = None,
                                      sale_start_date: Optional[datetime] = None,
                                      sale_end_date: Optional[datetime] = None,
                                      status: str = "active") -> PriceRead:
        """
        Update Product Price for a given country (async).
        
        Args:
            product_id: Numeric ID of the Product
            country: Country code
            price: Price of the product
            sale_price: Sale price of the product
            sale_start_date: Start date of a sale pricing
            sale_end_date: End date of a sale pricing
            status: Price status (active/inactive)
            
        Returns:
            The updated price information
        """
        payload = {}
        if price is not None:
            payload["price"] = price
        if sale_price is not None:
            payload["salePrice"] = sale_price
        if sale_start_date is not None:
            payload["saleStartDate"] = sale_start_date.isoformat() + "Z"
        if sale_end_date is not None:
            payload["saleEndDate"] = sale_end_date.isoformat() + "Z"
        if status:
            payload["status"] = status
        
        response_data = await self._client._make_request_async(
            "PUT", 
            f"/v2/product/{product_id}/prices/{country}", 
            json_data=payload
        )
        
        return PriceRead(**response_data)
    
    def update_product_price_status(self, product_id: int, country: str, status: str) -> None:
        """
        Update Product Price status for a given country.
        
        Args:
            product_id: Numeric ID of the Product
            country: Country code
            status: Price status (active/inactive)
        """
        payload = {"status": status}
        
        self._client._make_request_sync(
            "PUT", 
            f"/v2/product/{product_id}/prices/{country}/status", 
            json_data=payload
        )
    
    async def update_product_price_status_async(self, product_id: int, country: str, status: str) -> None:
        """
        Update Product Price status for a given country (async).
        
        Args:
            product_id: Numeric ID of the Product
            country: Country code
            status: Price status (active/inactive)
        """
        payload = {"status": status}
        
        await self._client._make_request_async(
            "PUT", 
            f"/v2/product/{product_id}/prices/{country}/status", 
            json_data=payload
        )
    
    # Quality control methods
    
    def get_rejected_product_sets(self, product_set_ids: List[int]) -> List[RejectedProductSet]:
        """
        Get information about rejected product sets.
        
        Args:
            product_set_ids: List of ProductSet ids
            
        Returns:
            List of rejected product sets with rejection reasons
        """
        params = {"productSetIds[]": product_set_ids}
        
        response_data = self._client._make_request_sync(
            "GET", 
            "/v2/product-quality-control/rejected", 
            params=params
        )
        
        return [RejectedProductSet(**item) for item in response_data]
    
    async def get_rejected_product_sets_async(self, product_set_ids: List[int]) -> List[RejectedProductSet]:
        """
        Get information about rejected product sets (async).
        
        Args:
            product_set_ids: List of ProductSet ids
            
        Returns:
            List of rejected product sets with rejection reasons
        """
        params = {"productSetIds[]": product_set_ids}
        
        response_data = await self._client._make_request_async(
            "GET", 
            "/v2/product-quality-control/rejected", 
            params=params
        )
        
        return [RejectedProductSet(**item) for item in response_data]