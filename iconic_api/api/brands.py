from typing import Optional, List, Literal, Union
from .base_api_module import BaseAPIModule
from ..models import (
    Brand, 
    BrandAttribute,
    ListBrandsRequest
)

class BrandsAPI(BaseAPIModule):
    def list_brands(self, params: ListBrandsRequest) -> List[Brand]:
        """Get list of brands by filter."""
        response_data = self._client._make_request_sync("GET", "/v2/brands", params=params.to_api_params())
        return [Brand(**item) for item in response_data]

    async def list_brands_async(self, params: ListBrandsRequest) -> List[Brand]:
        """Get list of brands by filter (async)."""
        response_data = await self._client._make_request_async("GET", "/v2/brands", params=params.to_api_params())
        return [Brand(**item) for item in response_data]

    def get_brand_by_id(self, brand_id: int) -> Brand:
        """Get single brand by ID."""
        response_data = self._client._make_request_sync("GET", f"/v2/brands/{brand_id}")
        return Brand(**response_data)

    async def get_brand_by_id_async(self, brand_id: int) -> Brand:
        """Get single brand by ID (async)."""
        response_data = await self._client._make_request_async("GET", f"/v2/brands/{brand_id}")
        return Brand(**response_data)

    def get_brand_attributes(self, brand_id: int) -> List[BrandAttribute]:
        """Get mapped attribute options for the brand."""
        response_data = self._client._make_request_sync("GET", f"/v2/brands/{brand_id}/attributes")
        return [BrandAttribute(**item) for item in response_data]

    async def get_brand_attributes_async(self, brand_id: int) -> List[BrandAttribute]:
        """Get mapped attribute options for the brand (async)."""
        response_data = await self._client._make_request_async("GET", f"/v2/brands/{brand_id}/attributes")
        return [BrandAttribute(**item) for item in response_data]