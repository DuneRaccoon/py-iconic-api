import logging
from typing import Dict, Any, List, Optional, Union

from .base import IconicResource, PaginatedResponse
from ..models import (
    Brand,
    BrandAttribute,
    ProductSetRead,
    ListBrandsRequest,
)

logger = logging.getLogger(__name__)

class Brand(IconicResource):
    """
    Brand resource representing a single brand or a collection of brands.
    
    When initialized with data, it represents a specific brand.
    Otherwise, it represents the collection of all brands.
    """
    
    endpoint = "brands"
    model_class = Brand
    
    #: Cap on the pages ``list_all_brands`` will walk. Only a runaway guard, so
    #: a server that never advances its offset cannot spin forever - it must
    #: never be the thing that decides how many brands a caller sees. At the old
    #: value of 50 x 100 this truncated at exactly 5,000, which is roughly what a
    #: real seller has, and it did so silently.
    MAX_BRAND_PAGES = 500

    #: Rows per request while walking. The endpoint documents no maximum; 100 is
    #: the value the rest of this SDK uses and is known to be accepted.
    BRAND_WALK_PAGE_SIZE = 100

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

    def search_brands(self, name: Optional[str] = None, limit: int = 100, offset: int = 0,
                      **filters) -> PaginatedResponse["Brand"]:  # noqa: D401
        """One page of brands, with the total so a caller can say "100 of 5000".

        ``name`` is the API's own server-side search ("Search brands by name"),
        which is the only workable way to reach a specific brand on a seller with
        thousands of them: pulling the whole catalogue to filter it locally would
        be 50 sequential requests before anything could be shown.

        Returns a :class:`PaginatedResponse`, so ``len(page)`` is what came back
        and ``page.total_count`` is how many matched in total.
        """
        params = self._prepare_brand_params(dict(filters, limit=limit, offset=offset))
        if name:
            params["name"] = name
        url = "/v2/brands"

        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")

        response = self._client._make_request_sync("GET", url, params=params)
        pagination = self._extract_pagination_data(response, params)
        return PaginatedResponse(
            items=[Brand(client=self._client, data=item)
                   for item in self._extract_items(response)],
            **pagination,
        )

    async def search_brands_async(self, name: Optional[str] = None, limit: int = 100,
                                  offset: int = 0, **filters) -> PaginatedResponse["Brand"]:
        """One page of brands asynchronously. See :meth:`search_brands`."""
        params = self._prepare_brand_params(dict(filters, limit=limit, offset=offset))
        if name:
            params["name"] = name
        url = "/v2/brands"

        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")

        response = await self._client._make_request_async("GET", url, params=params)
        pagination = self._extract_pagination_data(response, params)
        return PaginatedResponse(
            items=[Brand(client=self._client, data=item)
                   for item in self._extract_items(response)],
            **pagination,
        )

    def list_all_brands(self, params: Union[Dict[str, Any], ListBrandsRequest, None] = None) -> List["Brand"]:
        """Every brand matching the filters, walking limit/offset for the caller.

        Only for genuinely small result sets. A seller can have thousands of
        brands, and this issues one request per 100 of them before it returns —
        do NOT call it to populate a picker. Use :meth:`search_brands` with the
        API's ``name`` filter for that.

        The walk stops on a short page, on a page that adds nothing new, or at
        ``MAX_BRAND_PAGES``.
        """
        params = self._prepare_brand_params(params)
        page_size = int(params.get("limit") or self.BRAND_WALK_PAGE_SIZE)
        offset = int(params.get("offset") or 0)

        brands: List["Brand"] = []
        seen = set()
        total: Optional[int] = None

        for _page in range(self.MAX_BRAND_PAGES):
            # search_brands rather than list_brands: it carries the envelope's
            # totalCount, which is what lets the walk know it has everything
            # instead of inferring it from a short page.
            page = self.search_brands(**dict(params, limit=page_size, offset=offset))
            total = page.total_count if total is None else total
            if not len(page):
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
            if total and len(brands) >= total:
                break
            offset += len(page)
        else:
            logger.warning(
                "list_all_brands stopped at the %s-page cap with %s brand(s) of a "
                "declared %s. The list is INCOMPLETE.",
                self.MAX_BRAND_PAGES, len(brands), total,
            )

        if total and len(brands) < total:
            logger.warning(
                "list_all_brands returned %s brand(s) but The Iconic declared %s; "
                "the list is incomplete.", len(brands), total,
            )
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
