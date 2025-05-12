from typing import List, Optional
from .base_api_module import BaseAPIModule
from ..models import (
    Category,
    CategoryTree, 
    CategoryAttribute,
    CategoryMapping,
    CategoryById
)

class CategoryAPI(BaseAPIModule):
    def get_category_tree(self) -> List[CategoryTree]:
        """Get categories tree."""
        response_data = self._client._make_request_sync("GET", "/v2/category/tree") # type: ignore
        return [CategoryTree(**item) for item in response_data]

    async def get_category_tree_async(self) -> List[CategoryTree]:
        """Get categories tree (async)."""
        response_data = await self._client._make_request_async("GET", "/v2/category/tree") # type: ignore
        return [CategoryTree(**item) for item in response_data]
        
    def get_category_attributes(self, category_id: int) -> List[CategoryAttribute]:
        """Get category attributes."""
        response_data = self._client._make_request_sync("GET", f"/v2/category/{category_id}/attributes") # type: ignore
        return [CategoryAttribute(**item) for item in response_data]

    async def get_category_attributes_async(self, category_id: int) -> List[CategoryAttribute]:
        """Get category attributes (async)."""
        response_data = await self._client._make_request_async("GET", f"/v2/category/{category_id}/attributes") # type: ignore
        return [CategoryAttribute(**item) for item in response_data]
    
    # ... Add other category methods like get_root_category, get_category_children etc.