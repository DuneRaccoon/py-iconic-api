from typing import Dict, Any, List, Optional, Union

from .base import IconicResource
from ..models import (
    Brand,
    BrandAttribute,
    ProductSetRead,
    ListBrandsRequest,
)

class Brand(IconicResource):
    """
    Brand resource representing a single brand or a collection of brands.
    
    When initialized with data, it represents a specific brand.
    Otherwise, it represents the collection of all brands.
    """
    
    endpoint = "brands"
    model_class = Brand
    
    #: Cap on the pages ``list_all_brands`` will walk. A seller sees a few
    #: hundred brands at most; this only exists so a server that never advances
    #: its offset cannot spin forever.
    MAX_BRAND_PAGES = 50

    @staticmethod
    def _prepare_brand_params(params) -> Dict[str, Any]:
        """Normalise brand filters and guarantee the two required query params.

        ``limit`` and ``offset`` are marked REQUIRED on GET /v2/brands, so a
        bare dict of filters is rejected by the API. ``ListBrandsRequest``
        supplies both from ``BaseRequestParamsModel``; a plain dict gets the
        same defaults here.
        """
        if isinstance(params, ListBrandsRequest):
            params = params.to_api_params()
        params = dict(params or {})
        params.setdefault("limit", 100)
        params.setdefault("offset", 0)
        return params

    def list_brands(self, params: Union[Dict[str, Any], ListBrandsRequest, None] = None) -> List["Brand"]:
        """List one page of brands.

        The 200 body is the ``{"items": [...], "pagination": {...}}`` envelope,
        NOT a bare array. Iterating the response directly walked the dict's KEYS
        and raised ``TypeError: argument after ** must be a mapping, not str``,
        so brand listing never worked at all.

        By default The Iconic returns only the brands available to this seller;
        pass ``include_inaccessible`` to see the rest.
        """
        params = self._prepare_brand_params(params)
        url = "/v2/brands"

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [Brand(client=self._client, data=item)
                    for item in self._extract_items(response)]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_brands_async(self, params: Union[Dict[str, Any], ListBrandsRequest, None] = None) -> List["Brand"]:
        """List one page of brands asynchronously. See :meth:`list_brands`."""
        params = self._prepare_brand_params(params)
        url = "/v2/brands"

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [Brand(client=self._client, data=item)
                    for item in self._extract_items(response)]
        else:
            raise TypeError("This method requires an asynchronous client")

    def list_all_brands(self, params: Union[Dict[str, Any], ListBrandsRequest, None] = None) -> List["Brand"]:
        """Every brand matching the filters, walking limit/offset for the caller.

        There is no paginating helper for this endpoint, and a picker that shows
        only the first page silently hides brands. The walk stops on a short
        page, on the declared ``totalCount``, or at ``MAX_BRAND_PAGES``.
        """
        params = self._prepare_brand_params(params)
        page_size = int(params.get("limit") or 100)
        offset = int(params.get("offset") or 0)

        brands: List["Brand"] = []
        seen = set()
        for _page in range(self.MAX_BRAND_PAGES):
            page = self.list_brands(dict(params, limit=page_size, offset=offset))
            if not page:
                break
            # Guard against a server that ignores offset: without this a stuck
            # endpoint would be re-read until MAX_BRAND_PAGES, returning the same
            # rows over and over.
            fresh = [brand for brand in page if brand.id not in seen]
            if not fresh:
                break
            seen.update(brand.id for brand in fresh)
            brands.extend(fresh)
            if len(page) < page_size:
                break
            offset += len(page)
        return brands
            
    def get_attributes(self) -> List[BrandAttribute]:
        """Get mapped attribute options for this brand."""
        if not self.id:
            raise ValueError("Cannot get attributes without a brand ID")
            
        url = f"/v2/brands/{self.id}/attributes"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [BrandAttribute(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_attributes_async(self) -> List[BrandAttribute]:
        """Get mapped attribute options for this brand asynchronously."""
        if not self.id:
            raise ValueError("Cannot get attributes without a brand ID")
            
        url = f"/v2/brands/{self.id}/attributes"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [BrandAttribute(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Helper methods
    
    def get_product_sets(self, **params) -> List["ProductSetRead"]:
        """Get product sets that belong to this brand."""
        if not self.id:
            raise ValueError("Cannot get product sets without a brand ID")
            
        from .product_set import ProductSet
        
        params["brand_ids"] = [self.id]
        
        product_set = ProductSet(client=self._client)
        return product_set.list(**params)
        
    async def get_product_sets_async(self, **params) -> List["ProductSetRead"]:
        """Get product sets that belong to this brand asynchronously."""
        if not self.id:
            raise ValueError("Cannot get product sets without a brand ID")
            
        from .product_set import ProductSet
        
        params["brand_ids"] = [self.id]
        
        product_set = ProductSet(client=self._client)
        return await product_set.list_async(**params)
