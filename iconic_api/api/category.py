from typing import List, Optional, Dict, Any, Union
from .base_api_module import BaseAPIModule
from ..models import (
    Category,
    CategoryTree, 
    CategoryAttribute,
    CategoryMapping,
    CategoryById,
    CategorySetting,
    BaseRequestParamsModel
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
    
    def get_root_category(self) -> Category:
        """Get root category."""
        response_data = self._client._make_request_sync("GET", "/v2/category/root") # type: ignore
        return Category(**response_data)

    async def get_root_category_async(self) -> Category:
        """Get root category (async)."""
        response_data = await self._client._make_request_async("GET", "/v2/category/root") # type: ignore
        return Category(**response_data)
    
    def get_category_by_id(self, category_id: int) -> CategoryById:
        """Get category by ID."""
        response_data = self._client._make_request_sync("GET", f"/v2/category/{category_id}") # type: ignore
        return CategoryById(**response_data)

    async def get_category_by_id_async(self, category_id: int) -> CategoryById:
        """Get category by ID (async)."""
        response_data = await self._client._make_request_async("GET", f"/v2/category/{category_id}") # type: ignore
        return CategoryById(**response_data)
    
    def get_category_children(self, category_id: int) -> List[Category]:
        """Get category's direct children."""
        response_data = self._client._make_request_sync("GET", f"/v2/category/{category_id}/children") # type: ignore
        return [Category(**item) for item in response_data]

    async def get_category_children_async(self, category_id: int) -> List[Category]:
        """Get category's direct children (async)."""
        response_data = await self._client._make_request_async("GET", f"/v2/category/{category_id}/children") # type: ignore
        return [Category(**item) for item in response_data]
    
    def get_category_settings(self, category_id: int) -> List[CategorySetting]:
        """Get category settings."""
        response_data = self._client._make_request_sync("GET", f"/v2/category/{category_id}/settings") # type: ignore
        return [CategorySetting(**item) for item in response_data]

    async def get_category_settings_async(self, category_id: int) -> List[CategorySetting]:
        """Get category settings (async)."""
        response_data = await self._client._make_request_async("GET", f"/v2/category/{category_id}/settings") # type: ignore
        return [CategorySetting(**item) for item in response_data]
    
    def get_category_mappings(self) -> List[CategoryMapping]:
        """Get the all category-to-attribute mapping information."""
        response_data = self._client._make_request_sync("GET", "/v2/category/mappings") # type: ignore
        return [CategoryMapping(**item) for item in response_data]

    async def get_category_mappings_async(self) -> List[CategoryMapping]:
        """Get the all category-to-attribute mapping information (async)."""
        response_data = await self._client._make_request_async("GET", "/v2/category/mappings") # type: ignore
        return [CategoryMapping(**item) for item in response_data]
    
    def get_automatic_nomenclature(self, category_id: int) -> str:
        """Get formula for calculating automatic nomenclature."""
        response_data = self._client._make_request_sync("GET", f"/v2/category/{category_id}/automatic-nomenclature") # type: ignore
        # Response is a string, not an object
        return response_data

    async def get_automatic_nomenclature_async(self, category_id: int) -> str:
        """Get formula for calculating automatic nomenclature (async)."""
        response_data = await self._client._make_request_async("GET", f"/v2/category/{category_id}/automatic-nomenclature") # type: ignore
        # Response is a string, not an object
        return response_data
   