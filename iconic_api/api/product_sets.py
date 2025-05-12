from typing import Optional, List, Dict, Any, Union, TypeVar, Generic

from .base_api_module import BaseAPIModule
from ..models import (
    ProductSetRead,
    ProductSetCreated,
    ListProductSetsRequest,
    CreateProductSetRequest
)

T = TypeVar('T')

class PaginatedResponse(Generic[T]):
    """Generic class for paginated responses."""
    def __init__(self, items: List[T], limit: int, offset: int, total_count: int):
        self.items = items
        self.limit = limit
        self.offset = offset
        self.total_count = total_count

class ProductSetsAPI(BaseAPIModule):
    def list_product_sets(self, params: ListProductSetsRequest) -> PaginatedResponse[ProductSetRead]:
        """
        Get list of ProductSets based on filter criteria.
        
        Args:
            params: Filter and pagination parameters
            
        Returns:
            A paginated response containing product sets
        """
        response_data = self._client._make_request_sync("GET", "/v2/product-sets", params=params.to_api_params())
        
        # Extract pagination data and create items list
        items = [ProductSetRead(**item) for item in response_data.get("items", [])]
        pagination = response_data.get("pagination", {})
        limit = pagination.get("limit", params.limit)
        offset = pagination.get("offset", params.offset)
        total_count = pagination.get("totalCount", len(items))
        
        return PaginatedResponse(items, limit, offset, total_count)

    async def list_product_sets_async(self, params: ListProductSetsRequest) -> PaginatedResponse[ProductSetRead]:
        """
        Get list of ProductSets based on filter criteria (async).
        
        Args:
            params: Filter and pagination parameters
            
        Returns:
            A paginated response containing product sets
        """
        response_data = await self._client._make_request_async("GET", "/v2/product-sets", params=params.to_api_params())
        
        # Extract pagination data and create items list
        items = [ProductSetRead(**item) for item in response_data.get("items", [])]
        pagination = response_data.get("pagination", {})
        limit = pagination.get("limit", params.limit)
        offset = pagination.get("offset", params.offset)
        total_count = pagination.get("totalCount", len(items))
        
        return PaginatedResponse(items, limit, offset, total_count)

    def create_product_set(self, payload: CreateProductSetRequest) -> ProductSetCreated:
        """
        Create a new product set with a single product/variation.
        
        Args:
            payload: The product set data to create
            
        Returns:
            The newly created product set
        """
        # Convert the payload to camelCase for API
        prepared_payload = self._prepare_payload(payload.model_dump(by_alias=True, exclude_none=True))
        
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/product-set", 
            json_data=prepared_payload
        )
        
        return ProductSetCreated(**response_data)

    async def create_product_set_async(self, payload: CreateProductSetRequest) -> ProductSetCreated:
        """
        Create a new product set with a single product/variation (async).
        
        Args:
            payload: The product set data to create
            
        Returns:
            The newly created product set
        """
        # Convert the payload to camelCase for API
        prepared_payload = self._prepare_payload(payload.model_dump(by_alias=True, exclude_none=True))
        
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/product-set", 
            json_data=prepared_payload
        )
        
        return ProductSetCreated(**response_data)
