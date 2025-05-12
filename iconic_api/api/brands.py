from typing import Optional, List, Literal, Union
from .base_api_module import BaseAPIModule
from ..models import BrandAttribute, Brand

class BrandsAPI(BaseAPIModule):
    def list_brands(
        self,
        limit: int = 100,
        offset: int = 0,
        name: Optional[str] = None,
        brand_ids: Optional[List[int]] = None,
        brand_uuids: Optional[List[str]] = None,
        include_inaccessible: Optional[bool] = None,
        restricted_only: Optional[bool] = None,
        sort: Optional[Literal["createdAt", "updatedAt", "name"]] = None,
        sort_dir: Optional[Literal["asc", "desc"]] = None
    ) -> List[Brand]:
        """Get list of brands by filter."""
        params = self._clean_params({
            "name": name,
            "brand_ids": brand_ids, # Will be converted to brandIds[] by clean_params
            "brand_uuids": brand_uuids, # Will be converted to brandUuids[]
            "include_inaccessible": include_inaccessible,
            "restricted_only": restricted_only,
            "sort": sort,
            "sort_dir": sort_dir,
            "limit": limit,
            "offset": offset,
        })
        response_data = self._client._make_request_sync("GET", "/v2/brands", params=params) # type: ignore
        return [Brand(**item) for item in response_data]

    async def list_brands_async(
        self,
        limit: int = 100,
        offset: int = 0,
        name: Optional[str] = None,
        brand_ids: Optional[List[int]] = None,
        brand_uuids: Optional[List[str]] = None,
        include_inaccessible: Optional[bool] = None,
        restricted_only: Optional[bool] = None,
        sort: Optional[Literal["createdAt", "updatedAt", "name"]] = None,
        sort_dir: Optional[Literal["asc", "desc"]] = None,
    ) -> List[Brand]:
        """Get list of brands by filter (async)."""
        params = self._clean_params({
            "name": name,
            "brand_ids": brand_ids,
            "brand_uuids": brand_uuids,
            "include_inaccessible": include_inaccessible,
            "restricted_only": restricted_only,
            "sort": sort,
            "sort_dir": sort_dir,
            "limit": limit,
            "offset": offset,
        })
        response_data = await self._client._make_request_async("GET", "/v2/brands", params=params) # type: ignore
        return [Brand(**item) for item in response_data]

    def get_brand_by_id(self, brand_id: int) -> Brand:
        """Get single brand by ID."""
        response_data = self._client._make_request_sync("GET", f"/v2/brands/{brand_id}") # type: ignore
        return Brand(**response_data)

    async def get_brand_by_id_async(self, brand_id: int) -> Brand:
        """Get single brand by ID (async)."""
        response_data = await self._client._make_request_async("GET", f"/v2/brands/{brand_id}") # type: ignore
        return Brand(**response_data)

    def get_brand_attributes(self, brand_id: int) -> List[BrandAttribute]:
        """Get mapped attribute options for the brand."""
        response_data = self._client._make_request_sync("GET", f"/v2/brands/{brand_id}/attributes") # type: ignore
        return [BrandAttribute(**item) for item in response_data]

    async def get_brand_attributes_async(self, brand_id: int) -> List[BrandAttribute]:
        """Get mapped attribute options for the brand (async)."""
        response_data = await self._client._make_request_async("GET", f"/v2/brands/{brand_id}/attributes") # type: ignore
        return [BrandAttribute(**item) for item in response_data]