from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from datetime import datetime

from .base import IconicResource
from ..utils import chunks
from ..models.stock import StockData, StockUpdateItem, StockUpdateRequest

#: ``PUT /v2/stock/product`` is a synchronous endpoint with a hard limit of 100 products
#: per call. The limit is prose in the endpoint description only -- the schema declares no
#: ``maxItems`` -- so it has to be enforced here.
STOCK_UPDATE_BATCH_SIZE = 100


def _normalise_stock_items(
    items: Union[List[Dict[str, Any]], List[StockUpdateItem], StockUpdateRequest]
) -> List[Dict[str, Any]]:
    """
    Coerce any accepted input shape into the bare JSON array the API expects.

    ``PUT /v2/stock/product`` takes a top-level array of ``{"productId": int,
    "quantity": int}`` objects -- no envelope, no other keys.

    Args:
        items: List of dicts, list of StockUpdateItem objects, or a StockUpdateRequest

    Returns:
        List of ``{"productId": int, "quantity": int}`` dictionaries

    Raises:
        TypeError: If an element is neither a dict nor a StockUpdateItem
        ValueError: If productId/quantity is missing or is not an integer
    """
    if isinstance(items, StockUpdateRequest):
        return items.to_api_params()

    rows: List[Dict[str, Any]] = []

    for item in items:
        if isinstance(item, StockUpdateItem):
            rows.append({"productId": item.product_id, "quantity": item.quantity})
            continue

        if not isinstance(item, dict):
            raise TypeError(
                f"Stock update items must be dicts or StockUpdateItem objects, got {type(item).__name__}"
            )

        product_id = item.get("productId", item.get("product_id"))
        quantity = item.get("quantity")

        if product_id is None:
            raise ValueError(f"Stock update item is missing 'productId': {item!r}")
        if quantity is None:
            raise ValueError(f"Stock update item is missing 'quantity': {item!r}")

        # The API rejects string ids/quantities; callers frequently hold them as text
        # (Odoo stores the Iconic product id in a Char field), so coerce here rather
        # than shipping a body that silently fails validation server-side.
        try:
            rows.append({"productId": int(product_id), "quantity": int(quantity)})
        except (TypeError, ValueError):
            raise ValueError(
                f"Stock update item must have integer 'productId' and 'quantity': {item!r}"
            )

    return rows


def _resolve_batch_size(batch_size: int) -> int:
    """Validate a caller supplied batch size against the endpoint's hard limit."""
    if batch_size < 1 or batch_size > STOCK_UPDATE_BATCH_SIZE:
        raise ValueError(
            f"batch_size must be between 1 and {STOCK_UPDATE_BATCH_SIZE} "
            f"(the limit of PUT /v2/stock/product), got {batch_size}"
        )
    return batch_size


def _extract_failed_items(response: Any) -> List[StockUpdateItem]:
    """
    Parse one ``PUT /v2/stock/product`` response into the list of REJECTED items.

    The 200 body lists the products that could NOT be updated, not the ones that
    were. An empty array means every item in the batch was accepted. The transport
    returns ``{}`` for an empty body, so a non-list response is treated as success.
    """
    if not isinstance(response, list):
        return []
    return [StockUpdateItem(**item) for item in response]


class Stock(IconicResource):
    """
    Stock resource for managing product inventory levels.

    This resource provides methods to retrieve stock information for products
    and product sets, as well as update stock levels for products.
    """

    endpoint = "stock"
    model_class = None  # No specific model for the resource itself

    def get_product_stock(self, product_id: int) -> StockData:
        """
        Get stock information for a specific product.

        Args:
            product_id: The ID of the product to get stock for

        Returns:
            StockData object containing product stock information
        """
        url = f"/v2/stock/product/{product_id}"

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            # Add the product_id to the response for reference
            response["product_id"] = product_id
            return StockData(**response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_product_stock_async(self, product_id: int) -> StockData:
        """
        Get stock information for a specific product asynchronously.

        Args:
            product_id: The ID of the product to get stock for

        Returns:
            StockData object containing product stock information
        """
        url = f"/v2/stock/product/{product_id}"

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            # Add the product_id to the response for reference
            response["product_id"] = product_id
            return StockData(**response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def get_product_set_stock(self, product_set_id: int) -> List[StockData]:
        """
        Get stock information for all products in a product set.

        Note that the rows of ``GET /v2/stock/product-set/{productSetId}`` carry
        ``sellerSku`` / ``shopSku`` but NO ``productId`` -- join them back to product
        ids through ``ProductSet.get_products()`` on ``sellerSku``.

        Args:
            product_set_id: The ID of the product set to get stock for

        Returns:
            List of StockData objects containing product stock information
        """
        url = f"/v2/stock/product-set/{product_set_id}"

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [StockData(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_product_set_stock_async(self, product_set_id: int) -> List[StockData]:
        """
        Get stock information for all products in a product set asynchronously.

        Args:
            product_set_id: The ID of the product set to get stock for

        Returns:
            List of StockData objects containing product stock information
        """
        url = f"/v2/stock/product-set/{product_set_id}"

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [StockData(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")

    def update_stock(
        self,
        items: Union[List[Dict[str, Any]], List[StockUpdateItem], StockUpdateRequest],
        batch_size: int = STOCK_UPDATE_BATCH_SIZE,
    ) -> List[StockUpdateItem]:
        """
        Update stock levels for one or more products.

        ``PUT /v2/stock/product`` accepts at most 100 items per call, so anything longer
        is split into consecutive batches of ``batch_size`` and the per-batch results are
        concatenated. Callers do not need to chunk themselves.

        **The returned list is the FAILURES, not the successes.** The API's own wording:
        "If some of the products cannot be updated they will be ignored and only the
        others will be updated. In the response, there will be a list of those ignored
        products, the update of which has failed." An empty list therefore means every
        item was accepted; anything in it is a product whose stock was NOT changed
        (a product fulfilled by the venture, for example, can never be updated this way).

        Because the batches are separate HTTP calls, a failure part-way through leaves
        the earlier batches applied. That is safe to retry: the endpoint is a plain
        absolute-quantity write, so re-sending the same rows is idempotent.

        Args:
            items: Items to update, either as:
                  - List of dictionaries with productId and quantity
                  - List of StockUpdateItem objects
                  - StockUpdateRequest object containing items
            batch_size: Items per request, 1..100 (default 100)

        Returns:
            The items the API refused to update, across every batch. Empty on full success.
        """
        url = "/v2/stock/product"

        data = _normalise_stock_items(items)
        batch_size = _resolve_batch_size(batch_size)

        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")

        failed: List[StockUpdateItem] = []

        for batch in chunks(data, batch_size):
            response = self._client._make_request_sync("PUT", url, json_data=batch)
            failed.extend(_extract_failed_items(response))

        return failed

    async def update_stock_async(
        self,
        items: Union[List[Dict[str, Any]], List[StockUpdateItem], StockUpdateRequest],
        batch_size: int = STOCK_UPDATE_BATCH_SIZE,
    ) -> List[StockUpdateItem]:
        """
        Update stock levels for one or more products asynchronously.

        Anything longer than ``batch_size`` (max 100, the endpoint's own limit) is split
        into consecutive batches and the per-batch results are concatenated.

        **The returned list is the FAILURES, not the successes** -- see ``update_stock``.

        Args:
            items: Items to update, either as:
                  - List of dictionaries with productId and quantity
                  - List of StockUpdateItem objects
                  - StockUpdateRequest object containing items
            batch_size: Items per request, 1..100 (default 100)

        Returns:
            The items the API refused to update, across every batch. Empty on full success.
        """
        url = "/v2/stock/product"

        data = _normalise_stock_items(items)
        batch_size = _resolve_batch_size(batch_size)

        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")

        failed: List[StockUpdateItem] = []

        for batch in chunks(data, batch_size):
            response = await self._client._make_request_async("PUT", url, json_data=batch)
            failed.extend(_extract_failed_items(response))

        return failed
