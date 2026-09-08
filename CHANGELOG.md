# Changelog

All notable changes to `py-iconic-api` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Every endpoint, parameter and field claim below was checked against
`sc-api-schemas/iconic_api_full.json` (OpenAPI 3.0.3, server
`https://sellercenter-api.theiconic.com.au`).

## [0.2.0] - 2026-09-07

### BREAKING: `IconicResource.__getattr__` no longer fabricates HTTP calls

This is the headline fix and the reason for the minor-version bump.

Up to 0.1.21, `IconicResource.__getattr__` (`iconic_api/resources/base.py`) ended with:

```python
if self.id:
    ...
    def dynamic_endpoint(*args, **kwargs):
        path = f"{self._build_url(self.id)}/{name.replace('_', '/')}"
        return self._client._make_request_sync("GET", path, params=kwargs)
    return dynamic_endpoint
```

Any attribute miss on an instance that had a truthy `id` therefore returned a callable
that issued a **real HTTP GET against a made-up path**, instead of raising
`AttributeError`. The consequences:

- A mistyped or non-existent method name silently "worked". `order.set_items_ready_to_shipp(...)`
  did not raise; it issued `GET /v2/orders/{id}/set/items/ready/to/shipp` and returned
  whatever came back. This is how four order write-back endpoints that **do not exist in
  the API** (`/v2/orders/{orderNumber}/status`, `/packed`, `/shipment`, `/cancel`) shipped
  unnoticed for an entire release.
- `hasattr(resource, anything)` was unconditionally `True` for any instance with an id,
  so feature detection on a resource was meaningless.
- Collection-level resources (`client.orders`) *did* raise, while fetched instances
  (`client.orders.get(123)`) did not — so unit tests passed and only production broke.
- Reading `self._model` from inside `__getattr__` could recurse until `RecursionError`
  when an attribute was probed before `__init__` finished (`copy.deepcopy`, `pickle`,
  pydantic's arbitrary-type validation).

**Now:** an unknown attribute raises `AttributeError` like normal Python. The legitimate
parts of `__getattr__` are unchanged — the wrapped pydantic model is still consulted
first, then the raw `_data` payload. The private slots and dunder probes are answered
without re-entering `self`, so the recursion hazard is gone. The dead "related resource
class" branch (whose relative import could never resolve) was removed with it.

**Migration:** any call that relied on the fabrication now raises. There was exactly one
in the SDK (`ProductSet.get_products` — see below), and it was already dead code. If you
depended on a fabricated endpoint, add a real method after confirming the path exists in
the OpenAPI spec.

### Removed

- `ProductSet.get_products` / `get_products_async` / `get_product` / `get_product_async`
  were each **defined twice**. The first pair (formerly `product_set.py:41-79`) called
  `self.products()`, which only existed via the `__getattr__` fabrication, and was
  shadowed at import time by the correct pair further down the class. The dead pair is
  gone; the surviving implementations hit `GET /v2/product-set/{productSetId}/products`
  and `GET /v2/product-set/{productSetId}/products/{productId}`. Note that the dead
  `get_product` also passed `productId` as a *query* parameter rather than a path
  segment — evidence the fabricated calls were already silently wrong.

### Fixed — finance

Six methods could never return successfully: they built a generated pydantic model whose
required fields the documented response does not contain, so every call raised
`ValidationError`. Each was reproduced against a spec-derived body before the fix.

- `get_current_statement` / `_async` now return `CurrentFinanceStatement`.
  `GET /v2/finance/statements/current/{country}` has **no `id`** (the open statement is
  addressed as id `0` elsewhere), and `FinanceStatement.id` is required.
- `get_future_statements` / `_async` now return `FutureFinanceStatement`.
  `GET /v2/finance/statements/future/{country}` returns `payout` (not `payoutAmount`),
  `dueAt` (not `dueDate`), `guaranteeDeposit` as a *string*, and carries neither
  `country` nor `type`.
- `get_current_statement_details` / `get_future_statement_details` (and their `_async`
  twins) now return `TypedFinanceStatementDetails`. Those responses carry `type` and no
  `country`, while `FinanceStatementDetails.country` is required.
- `list_order_item_transactions` / `_async` now parse rows into
  `FinanceOrderItemTransaction` instead of wrapping them in the `Transaction` resource
  (whose `model_class` is `FinanceTransaction`). No `order-item-transactions` row has
  `FinanceTransaction`'s required `id` / `date` / `typeId` / `amount` fields.
- `list_transactions_v2` / `_async` now parse rows into `FinanceTransactionsV21`, for the
  same reason.
- `get_account_statement_groups` / `_async` now return `TransactionAccountStatementGroup`.
  `GET /v2/finance/transactions/account-statement-groups` is keyed by
  `accountStatementGroupId`; the two-field `AccountStatementGroup` model is the nested
  object from a v2.1 transaction row, not this endpoint's shape.
- `create_transaction` / `_async` now return the legacy `Transaction` model. The 201 body
  of `POST /v2/finance/transaction` is the legacy shape (`value`, `taxesVat`,
  `transactionStatementId`, `ref`), not a v2.1 transaction — parsing it as
  `FinanceTransactionsV21` raised **after** the write had already landed.
- `list_variables_async` validated nothing: its
  `isinstance(params, TransactionVariablesListParamsModel)` branch could never fire,
  because `**params` always arrives as a dict. It now validates exactly like its sync
  twin, so both send the same query string.

`FinanceStatement`, `FinanceStatementDetails` and `FinanceTransaction` remain correct for
the closed-statement and `/v2/finance/transactions` endpoints and are unchanged.

### Fixed — stock

- `Stock.update_stock` / `_async` **chunk automatically**. `PUT /v2/stock/product` accepts
  at most 100 items; the previous behaviour was to raise `ValueError` and leave every
  caller to reimplement batching. Anything longer is now split into batches of
  `batch_size` (default and maximum 100) and the per-batch results are concatenated.
- The **return value's meaning is documented and now honoured**: the 200 body of
  `PUT /v2/stock/product` is the list of items the API **refused** to update, not the
  ones it accepted ("If some of the products cannot be updated they will be ignored ...
  In the response, there will be a list of those ignored products"). The docstring
  previously said "List of successful stock updates" — the exact opposite.
- Input is normalised and validated up front: dicts (`productId` or `product_id`),
  `StockUpdateItem` objects and `StockUpdateRequest` are all accepted, ids and quantities
  are coerced to `int` (callers commonly hold the product id as text), and a missing or
  non-numeric value raises instead of producing a body the server rejects.
- The verified body shape is a bare JSON array of `{"productId": int, "quantity": int}` —
  no envelope. A non-list response (the transport returns `{}` for an empty body) is
  treated as full success.

### Fixed — product

- `Product.get` / `get_async` no longer build `GET /v2/product/{productId}`, **which does
  not exist** in the spec. They now use `GET /v2/products?productIds[]={id}` and raise
  `ValueError` when nothing comes back. The other supported single-variant lookups remain
  `get_by_seller_sku`, `get_by_shop_sku` and `ProductSet.get_product`.
- `Product.update_stock` / `_async` return `bool` instead of a `StockUpdateItem`. They
  used to return `result[0]` — a row from the *failure* list — as though it were proof the
  write had landed, which inverted the meaning of the call. `True` now means the API
  accepted the update.
- `update_price` / `_async` accept aware datetimes correctly. `sale_start_date.isoformat()
  + "Z"` produced the invalid `...+00:00Z` for a timezone-aware value; dates are now
  converted to UTC and suffixed once. Strings are passed through untouched. The docstring
  now carries the endpoint's null-on-omission rule: every price field you omit is written
  as NULL and only `status` survives, so a partial update silently wipes an active sale.
  `status` is typed `Literal["active", "inactive"]`.
- `update` / `_async` reject fields the endpoint discards.
  `PUT /v2/product-set/{productSetId}/products/{productId}` acts only on `sellerSku`,
  `status`, `variation`, `shipmentTypeId`, `productIdentifier` and `name` — "Other
  attributes will be discarded" — and a delete/undelete makes it ignore every other field
  in the same request. Both rules failed silently server-side and now raise `ValueError`.
- `list_by_seller_skus` / `_async` reject more than 100 SKUs, the endpoint's documented
  maximum, instead of letting the request fail server-side.
- `update_status` / `_async` were already correct — `status` is a **query** parameter on
  `PUT /v2/product-set/{productSetId}/products/{productId}/status` and there is no request
  body — and are now typed `Literal["active", "inactive", "deleted"]` and documented as
  such so the pattern is not "corrected" into a JSON body later.
- `update_price_status` / `_async` were also already correct: this one *does* take a JSON
  body and answers 204 No Content.

### Added

- `Finance.paginate_statements` / `paginate_statements_async` — generators that walk
  limit/offset. `list_statements` discards the `pagination` envelope and so can never see
  past the first page.
- `CurrentFinanceStatement`, `FutureFinanceStatement` and `TypedFinanceStatementDetails`
  response models, defined in `iconic_api/resources/finance.py`.
- `iconic_api.resources.stock.STOCK_UPDATE_BATCH_SIZE` (100) and a `batch_size` argument
  on `update_stock` / `update_stock_async`.
- `iconic_api.resources.product.PRODUCT_WRITABLE_FIELDS` and
  `MAX_SELLER_SKUS_PER_REQUEST`.

### Documentation

- `Finance.list_transactions_v2` / `_async` carry a prominent warning that
  `GET /v2.1/finance/transactions` **cannot** be used for order-item-level payout
  matching. Despite being the newer version it **dropped `orderItemId`**, leaving only
  `orderNumber`, `productSku` and an undiscriminated `transactionReference`
  ("Can be related to an order, order item, product, seller or other") with no companion
  field saying which. Use `GET /v2/finance/order-item-transactions` (which has
  `orderItemId` + `orderId` + `payoutAmount` + `payoutStatus`) as the reconciliation
  grain and `GET /v2/finance/transactions` (which still has `orderItemId`) for the
  per-transaction-type ledger. The v2/v2.1 filter-name divergences
  (`startDate`/`endDate` vs `gteCreatedAt`/`lteCreatedAt`, `product[]` vs `products[]`,
  `typeIds[]` vs `transactionTypeIds[]`) are documented alongside.
- `list_transactions` documents that the product filter is the **singular** `product[]` —
  passing `products[]` is silently ignored and returns the entire unfiltered ledger.
- `list_order_item_transactions` documents that there is no `orderItemIds[]` filter, that
  the rows carry no `orderNumber`, and that `statementId == 0` means the **current, open**
  statement rather than "no statement" (so any falsy check discards the whole open period).
- `Stock.get_product_set_stock` documents that its rows carry no `productId` and must be
  joined back on `sellerSku`.

### Known issues (not fixed here — they live in files outside this change)

- `iconic_api/models/stock.py`: `StockUpdateItem` has no `populate_by_name`, so
  `StockUpdateItem(product_id=1, quantity=2)` raises; only the `productId` alias works.
- `iconic_api/models/openapi_generated.py`: the `Image` model is the wrong schema (the
  images sub-object of `HybridProduct`), so `ProductSet.get_images()` / `add_image()` /
  `upload_image()` raise `ValidationError` on a real response — `position` is `int` in the
  API and `Optional[str]` in the model.
- `iconic_api/models/api_requests.py`: `BaseRequestParamsModel` injects `limit: int = 100`
  and `offset: int = 0`, which leak into POST/PUT JSON **bodies** built from request models.
- `iconic_api/client.py`: sync request signing builds the signed string without a `?`
  before the query, so `requires_signing=True` produces a wrong signature on the sync path.
- `iconic_api/resources/product_set.py`: `create_product_set` / `update_product_set` wrap
  the attribute-helper block in `except Exception: log warning`, so a mapping failure still
  POSTs an invalid payload.
- `PUT /v2/product-set/{productSetId}/prices` (bulk prices) and the image `PATCH`/`DELETE`
  endpoints have no SDK methods yet, and no `/v2/import/*` or `/v2/feed/*` endpoint is
  implemented.

## [0.1.21] and earlier

No changelog was kept before 0.2.0; see the git history.
