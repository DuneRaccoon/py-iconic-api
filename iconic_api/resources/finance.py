from typing import AsyncGenerator, Dict, Any, List, Literal, Optional, Union, Generator
from datetime import datetime

from pydantic import BaseModel, Field

from .base import IconicResource, T
from .transaction import Transaction
from ..models import (
    Transaction as TransactionModel,
    Details,
    FinanceStatement,
    FinanceStatementListParamsModel,
    FinanceStatementDetails,
    FinanceOrderItemTransaction,
    FinanceTransactionsV21,
    TransactionType,
    TransactionAccountStatementGroup,
    TransactionVariablesListParamsModel
)

StatementType = Literal["marketplace", "consignment"]


# ----------------------------------------------------------------------------------
# Response models for the statement variants the generated models do not cover.
#
# `FinanceStatement` and `FinanceStatementDetails` are generated from the CLOSED
# statement schemas (`/v2/finance/statements[/{id}][/details]`). The current/{country}
# and future/{country} variants return genuinely different objects, and feeding those
# bodies to the generated models raises pydantic ValidationError every single time --
# which is why `get_current_statement`, `get_future_statements`,
# `get_current_statement_details` and `get_future_statement_details` could never
# return successfully before 0.2.0.
# ----------------------------------------------------------------------------------

class CurrentFinanceStatement(BaseModel):
    """
    The open, not-yet-closed statement: ``GET /v2/finance/statements/current/{country}``.

    Differs from :class:`FinanceStatement` by having **no ``id``** -- the current
    statement is addressed as id ``0`` by every other finance endpoint -- and by making
    ``country`` optional. It also carries ``paymentRef`` / ``uploadId``, which the
    closed-statement schema does not have.
    """

    sellerId: int
    number: str
    startDate: datetime
    endDate: datetime
    openingBalance: float
    closingBalance: float
    payoutAmount: float
    guaranteeDeposit: float
    currency: str = Field(..., description="Three-letter code, ISO 4217 standard.")
    type: StatementType
    country: Optional[str] = None
    paid: Optional[bool] = None
    note: Optional[str] = None
    paymentRef: Optional[str] = None
    uploadId: Optional[str] = None
    paidAt: Optional[datetime] = None
    dueDate: Optional[datetime] = None


class FutureFinanceStatement(BaseModel):
    """
    A projected statement: ``GET /v2/finance/statements/future/{country}``.

    Three field names differ from every other statement shape -- ``payout`` (not
    ``payoutAmount``), ``dueAt`` (not ``dueDate``) -- and there is no ``country`` and no
    ``type``. ``guaranteeDeposit`` is typed as a *string* on this endpoint alone, so it
    is accepted as either.
    """

    id: int
    sellerId: int
    number: Optional[str] = None
    uuid: Optional[str] = None
    startDate: datetime
    endDate: datetime
    openingBalance: float
    closingBalance: Optional[float] = None
    payout: Optional[float] = None
    guaranteeDeposit: Optional[Union[str, float]] = None
    currency: str
    paid: bool
    note: Optional[str] = None
    userId: Optional[int] = None
    paymentRef: Optional[str] = None
    uploadId: Optional[int] = None
    paidAt: Optional[datetime] = None
    dueAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime


class TypedFinanceStatementDetails(BaseModel):
    """
    Statement section totals for a current or future statement.

    ``GET /v2/finance/statements/current/{country}/details`` and
    ``.../future/{country}/details`` return ``type`` where the closed-statement variant
    returns ``country``. The ``details`` tree itself is identical, so it reuses the
    generated :class:`Details` model.

    Every ``groups[].id`` inside ``details`` is a **transaction type id**, not an
    account-statement-group id -- join it to ``GET /v2/finance/transaction/types``, not
    to ``GET /v2/finance/transactions/account-statement-groups``.
    """

    id: int
    currency: str
    type: StatementType
    details: Details


class Finance(IconicResource):
    """
    Finance resource for managing financial statements and related data.
    
    Provides methods for accessing finance statements, their details, and more.
    """
    
    endpoint = "finance"
    model_class = None  # No specific model for the resource itself

    @staticmethod
    def _parse_transaction_page(response: Any, model: type) -> Dict[str, Any]:
        """
        Parse a ``{items, pagination}`` finance envelope into typed rows.

        Each finance list endpoint returns a DIFFERENT row shape, so the model is passed
        in per call site. Wrapping every one of them in the ``Transaction`` resource --
        whose ``model_class`` is ``FinanceTransaction`` -- was how ``list_transactions_v2``
        and ``list_order_item_transactions`` came to raise pydantic ValidationError on
        every single row: neither response carries ``FinanceTransaction``'s required
        ``id`` / ``date`` / ``typeId`` / ``amount`` fields.

        Args:
            response: The raw decoded body
            model: The pydantic model matching this endpoint's row shape

        Returns:
            The response dict with ``items`` replaced by parsed models, or the raw
            response unchanged when it is not the paginated envelope
        """
        if isinstance(response, dict) and "items" in response:
            result = response.copy()
            result["items"] = [model(**item) for item in response["items"]]
            return result

        return response

    def list_statements(self, **params: Union[Dict[str, Any], FinanceStatementListParamsModel]) -> List[FinanceStatement]:
        """
        Get ONE PAGE of finance statements based on specified parameters.

        The ``pagination`` envelope is discarded, so this returns at most ``limit``
        statements (100 by default) no matter how many exist. Use
        ``paginate_statements`` when you need them all.

        A statement whose ``id`` is ``0`` is the CURRENT, still-open period -- never
        treat it as a closed, payable statement.

        Args:
            **params: Union[Dict[str, Any], FinanceStatementListParamsModel]
        Returns:
            List of finance statements
        """

        if isinstance(params, dict):
            params = FinanceStatementListParamsModel(**params)
            
        params = params.model_dump(exclude_none=True)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        response = self._client._make_request_sync("GET", "/v2/finance/statements", params=params)
        
        return [
            FinanceStatement(**item) for item in response.get("items", [])
        ]

    def paginate_statements(self, **params: Any) -> Generator[FinanceStatement, None, None]:
        """
        Yield every finance statement matching the filters, walking limit/offset.

        ``list_statements`` throws the ``pagination`` envelope away and so can never see
        past the first page; this generator keeps requesting until a short page comes
        back.

        Args:
            **params: The same filters as ``list_statements``; ``limit`` sets the page size

        Yields:
            Finance statements, one at a time, oldest page first
        """
        limit = int(params.get("limit") or 100)
        offset = int(params.get("offset") or 0)

        while True:
            params["limit"] = limit
            params["offset"] = offset

            page = self.list_statements(**params)

            if not page:
                break

            for statement in page:
                yield statement

            if len(page) < limit:
                break

            offset += limit

    async def paginate_statements_async(self, **params: Any) -> AsyncGenerator[FinanceStatement, None]:
        """
        Yield every finance statement matching the filters asynchronously, walking limit/offset.

        Args:
            **params: The same filters as ``list_statements``; ``limit`` sets the page size

        Yields:
            Finance statements, one at a time, oldest page first
        """
        limit = int(params.get("limit") or 100)
        offset = int(params.get("offset") or 0)

        while True:
            params["limit"] = limit
            params["offset"] = offset

            page = await self.list_statements_async(**params)

            if not page:
                break

            for statement in page:
                yield statement

            if len(page) < limit:
                break

            offset += limit

    async def list_statements_async(self, **params: Union[Dict[str, Any], FinanceStatementListParamsModel]) -> List[FinanceStatement]:
        """
        Get ONE PAGE of finance statements based on specified parameters, asynchronously.

        The ``pagination`` envelope is discarded, so at most ``limit`` statements come
        back regardless of how many exist. A statement whose ``id`` is ``0`` is the
        CURRENT, still-open period.

        Args:
            **params: Query parameters for filtering the statements
                See list_statements for available parameters

        Returns:
            List of finance statements
        """

        if isinstance(params, dict):
            params = FinanceStatementListParamsModel(**params)
            
        params = params.model_dump(exclude_none=True)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        response = await self._client._make_request_async("GET", "/v2/finance/statements", params=params)
        
        return [
            FinanceStatement(**item) for item in response.get("items", [])
        ]
        
    def get_statement(self, statement_id: int) -> FinanceStatement:
        """
        Get a single finance statement by ID.
        
        Args:
            statement_id: ID of the finance statement to retrieve
            
        Returns:
            The finance statement
        """
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        response = self._client._make_request_sync("GET", f"/v2/finance/statements/{statement_id}")
        
        return FinanceStatement(**response)
            
    async def get_statement_async(self, statement_id: int) -> FinanceStatement:
        """
        Get a single finance statement by ID, asynchronously.
        
        Args:
            statement_id: ID of the finance statement to retrieve
            
        Returns:
            The finance statement
        """
        url = f"/v2/finance/statements/{statement_id}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return FinanceStatement(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_statement_details(self, statement_id: int) -> FinanceStatementDetails:
        """
        Get details of a single finance statement by ID.
        
        Args:
            statement_id: ID of the finance statement
            
        Returns:
            The finance statement details
        """
        url = f"/v2/finance/statements/{statement_id}/details"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return FinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_statement_details_async(self, statement_id: int) -> FinanceStatementDetails:
        """
        Get details of a single finance statement by ID, asynchronously.
        
        Args:
            statement_id: ID of the finance statement
            
        Returns:
            The finance statement details
        """
        url = f"/v2/finance/statements/{statement_id}/details"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return FinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_current_statement(self, country: str, statement_type: StatementType = "marketplace") -> CurrentFinanceStatement:
        """
        Get the current (open) finance statement for a specific country.

        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')

        Returns:
            The current finance statement. Note this is a :class:`CurrentFinanceStatement`,
            not a :class:`FinanceStatement`: the response has no ``id`` (the open statement
            is id ``0`` elsewhere), so it cannot be parsed as a closed statement.
        """
        url = f"/v2/finance/statements/current/{country}"
        params = {"type": statement_type}

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return CurrentFinanceStatement(**response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_current_statement_async(self, country: str, statement_type: StatementType = "marketplace") -> CurrentFinanceStatement:
        """
        Get the current (open) finance statement for a specific country, asynchronously.

        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')

        Returns:
            The current finance statement, as a :class:`CurrentFinanceStatement`
        """
        url = f"/v2/finance/statements/current/{country}"
        params = {"type": statement_type}

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return CurrentFinanceStatement(**response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def get_current_statement_details(self, country: str, statement_type: StatementType = "marketplace") -> TypedFinanceStatementDetails:
        """
        Get details of the current finance statement for a specific country.

        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')

        Returns:
            The current statement's section totals. This response carries ``type`` and
            no ``country``, so it is a :class:`TypedFinanceStatementDetails` rather than
            a :class:`FinanceStatementDetails`.
        """
        url = f"/v2/finance/statements/current/{country}/details"
        params = {"type": statement_type}

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return TypedFinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_current_statement_details_async(self, country: str, statement_type: StatementType = "marketplace") -> TypedFinanceStatementDetails:
        """
        Get details of the current finance statement for a specific country, asynchronously.

        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')

        Returns:
            The current statement's section totals, as a :class:`TypedFinanceStatementDetails`
        """
        url = f"/v2/finance/statements/current/{country}/details"
        params = {"type": statement_type}

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return TypedFinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires an asynchronous client")

    def get_future_statements(self, country: str, statement_type: StatementType = "marketplace") -> List[FutureFinanceStatement]:
        """
        Get collection of possible future statements with installment payments.

        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')

        Returns:
            List of projected statements. These are :class:`FutureFinanceStatement`
            objects: the endpoint returns ``payout`` (not ``payoutAmount``) and ``dueAt``
            (not ``dueDate``), and carries neither ``country`` nor ``type``.
        """
        url = f"/v2/finance/statements/future/{country}"
        params = {"type": statement_type}

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [FutureFinanceStatement(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_future_statements_async(self, country: str, statement_type: StatementType = "marketplace") -> List[FutureFinanceStatement]:
        """
        Get collection of possible future statements with installment payments, asynchronously.

        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')

        Returns:
            List of projected statements, as :class:`FutureFinanceStatement` objects
        """
        url = f"/v2/finance/statements/future/{country}"
        params = {"type": statement_type}

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [FutureFinanceStatement(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")

    def get_future_statement_details(self, country: str, start_date: datetime, end_date: datetime, statement_type: StatementType = "marketplace") -> TypedFinanceStatementDetails:
        """
        Get details of a concrete future statement.

        ``startDate`` and ``endDate`` are REQUIRED query parameters on this endpoint.

        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            start_date: Start date of the expected future statement
            end_date: End date of the expected future statement
            statement_type: Type of the statement ('marketplace' or 'consignment')

        Returns:
            The future statement's section totals, as a :class:`TypedFinanceStatementDetails`
        """
        url = f"/v2/finance/statements/future/{country}/details"
        params = {
            "type": statement_type,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat()
        }

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return TypedFinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_future_statement_details_async(self, country: str, start_date: datetime, end_date: datetime, statement_type: StatementType = "marketplace") -> TypedFinanceStatementDetails:
        """
        Get details of a concrete future statement, asynchronously.

        ``startDate`` and ``endDate`` are REQUIRED query parameters on this endpoint.

        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            start_date: Start date of the expected future statement
            end_date: End date of the expected future statement
            statement_type: Type of the statement ('marketplace' or 'consignment')

        Returns:
            The future statement's section totals, as a :class:`TypedFinanceStatementDetails`
        """
        url = f"/v2/finance/statements/future/{country}/details"
        params = {
            "type": statement_type,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat()
        }

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return TypedFinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def list_transactions(self, **params) -> Dict[str, Any]:
        """
        Returns a list of transactions for the specified period and statement IDs.

        ``GET /v2/finance/transactions`` is the per-transaction-type ledger and it DOES
        carry ``orderItemId`` -- unlike ``/v2.1/finance/transactions``, which dropped it.
        Use this (or ``list_order_item_transactions``) for payout attribution.

        Two filter-name traps: the product filter is the SINGULAR ``product[]`` here
        (``products[]`` is silently ignored and you get the whole unfiltered ledger back),
        and ``orderItemId`` is a single integer, not an array. ``statementId == 0`` on a
        returned row means the current, still-open statement.

        Args:
            statement_ids: List of IDs of the financial statements
            seller_id: ID of the seller (admin only)
            start_date: Start date for transactions
            end_date: End date for transactions
            source: Source of transactions ('sellercenter', 'web', 'csv')
            country: Country filter
            order_item_id: ID of the order item
            order_item_src_id: Source ID of the order item
            order_numbers: List of order numbers
            sort: Field to sort by ('id', 'date')
            sort_dir: Sort direction ('asc', 'desc')
            numbers: List of transaction numbers
            type_ids: List of transaction type IDs
            is_hybrid: Filter by order item is_hybrid field
            is_outlet: Filter by order item is_outlet field
            is_paid: Filter by paid statement
            product: Filter by product data (name/shop sku/seller sku)
            statement_type: Filter by statement type ('marketplace', 'consignment')
            limit: Maximum number of items to return
            offset: Offset for pagination
            
        Returns:
            Dict containing transactions list with Transaction objects and pagination info
        """
        url = "/v2/finance/transactions"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            
            # Convert transaction items to Transaction objects
            if isinstance(response, dict) and "items" in response:
                from .transaction import Transaction
                
                # Create Transaction objects but preserve pagination info
                result = response.copy()
                result["items"] = [Transaction(client=self._client, data=item) for item in response["items"]]
                return result
            
            return response
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_transactions_async(self, **params) -> Dict[str, Any]:
        """
        Returns a list of transactions for the specified period and statement IDs, asynchronously.
        
        Args:
            See list_transactions method for available parameters
            
        Returns:
            Dict containing transactions list with Transaction objects and pagination info
        """
        url = "/v2/finance/transactions"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            
            # Convert transaction items to Transaction objects
            if isinstance(response, dict) and "items" in response:
                from .transaction import Transaction
                
                # Create Transaction objects but preserve pagination info
                result = response.copy()
                result["items"] = [Transaction(client=self._client, data=item) for item in response["items"]]
                return result
                
            return response
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def paginate_transactions(self: T, **params) -> Generator["Transaction", None, None]:
        """Generator to paginate through transactions."""
        return self.paginate(url="/v2/finance/transactions", instance_cls=Transaction, **params)
    
    def list_transactions_v2(self, **params) -> Dict[str, Any]:
        """
        Returns a list of transactions by filter criteria (v2.1 API).

        .. warning::
           **This endpoint CANNOT be used for order-item-level payout matching.**
           Despite being the newer version, ``GET /v2.1/finance/transactions`` DROPPED
           ``orderItemId``. All it offers is ``orderNumber``, ``productSku`` and
           ``transactionReference`` -- and ``transactionReference`` is an undiscriminated
           integer, documented as "Can be related to an order, order item, product,
           seller or other", with no companion field saying which. Matching a payout to
           an order item through it is guesswork.

           Use ``list_order_item_transactions`` (``GET /v2/finance/order-item-transactions``,
           which carries ``orderItemId`` + ``orderId`` + ``payoutAmount`` + ``payoutStatus``)
           as the reconciliation grain, and ``list_transactions``
           (``GET /v2/finance/transactions``, which still carries ``orderItemId``) for the
           per-transaction-type ledger. Reach for v2.1 only when you specifically need
           ``accountStatementNumber``, ``accountStatementIsPaid``,
           ``accountStatementPaymentDueDate`` or ``ruleId`` denormalised onto the row.

        Other traps versus v2: the date filters are ``gteCreatedAt`` / ``lteCreatedAt``
        (not ``startDate`` / ``endDate``), the product filter is ``products[]`` (v2 uses
        the singular ``product[]``), the type filter is ``transactionTypeIds[]`` (v2 uses
        ``typeIds[]``), and ``source`` accepts a fourth value, ``api``.

        Args:
            statement_type: Filter by statement type ('marketplace', 'consignment')
            seller_id: Filter by seller ID (admin only)
            gte_created_at: Filter by creation date >= value
            lte_created_at: Filter by creation date <= value
            country: Filter by country
            source: Filter by source ('sellercenter', 'api', 'web', 'csv')
            order_item_ids: Filter by order item IDs
            order_item_src_ids: Filter by order item source IDs
            order_numbers: Filter by order numbers
            numbers: Filter by transaction numbers
            products: Filter by product data
            statement_id: Filter by statement ID (0 for current)
            transaction_type_ids: Filter by transaction type IDs
            is_outlet: Filter by order item is_outlet field
            is_hybrid: Filter by order item is_hybrid field
            is_paid: Filter by paid statement
            sort: Sort field ('createdAt', 'transactionType', 'transactionNumber', 'amount')
            sort_dir: Sort direction ('asc', 'desc')
            limit: Maximum number of items to return
            offset: Offset for pagination

        Returns:
            Dict with ``items`` (a list of :class:`FinanceTransactionsV21`) and ``pagination``
        """
        url = "/v2.1/finance/transactions"

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return self._parse_transaction_page(response, FinanceTransactionsV21)
        else:
            raise TypeError("This method requires a synchronous client")

    async def list_transactions_v2_async(self, **params) -> Dict[str, Any]:
        """
        Returns a list of transactions by filter criteria (v2.1 API), asynchronously.

        .. warning::
           **This endpoint CANNOT be used for order-item-level payout matching** -- v2.1
           dropped ``orderItemId``. See ``list_transactions_v2`` for the full explanation
           and for what to use instead.

        Args:
            See list_transactions_v2 method for available parameters

        Returns:
            Dict with ``items`` (a list of :class:`FinanceTransactionsV21`) and ``pagination``
        """
        url = "/v2.1/finance/transactions"

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return self._parse_transaction_page(response, FinanceTransactionsV21)
        else:
            raise TypeError("This method requires an asynchronous client")


    def list_order_item_transactions(self, **params) -> Dict[str, Any]:
        """
        Returns a list of order item transactions for the specified period.

        ``GET /v2/finance/order-item-transactions`` is the pre-aggregated per-item payout
        row -- ``orderItemId``, ``orderId``, ``commission``, ``fees``, ``vatAmount``,
        ``whtAmount``, ``payoutAmount``, ``statementId``, ``payoutStatus`` -- and is the
        right grain for reconciling a marketplace payout against Odoo order lines.

        Two things to know before filtering:

        * There is **no** ``orderItemIds[]`` filter. Pull a whole ``statementId`` (or a
          date range) and join on ``orderItemId`` client-side.
        * ``statementId == 0`` means the CURRENT, still-open statement -- not "no
          statement". Any falsy check on it silently discards the entire open period.
        * The rows carry no ``orderNumber``, even though ``orderNumbers[]`` is an
          accepted filter.

        Args:
            statement_id: Filter by statement ID
            start_date: Start date for transactions
            end_date: End date for transactions
            products: Filter by product data
            product_skus: Filter by product SKUs
            order_numbers: Filter by order numbers
            payout_status: Filter by payout status ('paid', 'unpaid', 'partiallyPaid')
            shipment_types: Filter by shipment types
            status: Filter by order item status
            is_hybrid: Filter by order item is_hybrid field
            is_outlet: Filter by order item is_outlet field
            statement_type: Filter by statement type
            limit: Maximum number of items to return
            offset: Offset for pagination
            sort: Field to sort by
            sort_dir: Sort direction ('asc', 'desc')

        Returns:
            Dict with ``items`` (a list of :class:`FinanceOrderItemTransaction`) and ``pagination``
        """
        url = "/v2/finance/order-item-transactions"

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return self._parse_transaction_page(response, FinanceOrderItemTransaction)
        else:
            raise TypeError("This method requires a synchronous client")

    async def list_order_item_transactions_async(self, **params) -> Dict[str, Any]:
        """
        Returns a list of order item transactions for the specified period, asynchronously.

        See ``list_order_item_transactions`` -- there is no ``orderItemIds[]`` filter, and
        ``statementId == 0`` is the current open statement rather than "no statement".

        Args:
            See list_order_item_transactions method for available parameters

        Returns:
            Dict with ``items`` (a list of :class:`FinanceOrderItemTransaction`) and ``pagination``
        """
        url = "/v2/finance/order-item-transactions"

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return self._parse_transaction_page(response, FinanceOrderItemTransaction)
        else:
            raise TypeError("This method requires an asynchronous client")


    def get_transaction_types(self) -> List[TransactionType]:
        """
        Get the entire list of transaction types.
        
        Returns:
            List of transaction types
        """
        url = "/v2/finance/transaction/types"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [TransactionType(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
    
    async def get_transaction_types_async(self) -> List[TransactionType]:
        """
        Get the entire list of transaction types, asynchronously.
        
        Returns:
            List of transaction types
        """
        url = "/v2/finance/transaction/types"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [TransactionType(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def get_account_statement_groups(self, statement_type: StatementType = "marketplace") -> List[TransactionAccountStatementGroup]:
        """
        Get the entire list of transaction account statement groups.

        The rows are :class:`TransactionAccountStatementGroup` -- keyed by
        ``accountStatementGroupId``, not ``id``. The two-field ``AccountStatementGroup``
        model this method used to build is the nested object from a v2.1 transaction row,
        not this endpoint's shape, so every row raised a pydantic ValidationError.

        Args:
            statement_type: Filter by statement type ('marketplace', 'consignment')

        Returns:
            List of account statement groups
        """
        url = "/v2/finance/transactions/account-statement-groups"
        params = {"statementType": statement_type}

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [TransactionAccountStatementGroup(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")

    async def get_account_statement_groups_async(self, statement_type: StatementType = "marketplace") -> List[TransactionAccountStatementGroup]:
        """
        Get the entire list of transaction account statement groups, asynchronously.

        Args:
            statement_type: Filter by statement type ('marketplace', 'consignment')

        Returns:
            List of account statement groups, as :class:`TransactionAccountStatementGroup`
        """
        url = "/v2/finance/transactions/account-statement-groups"
        params = {"statementType": statement_type}

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [TransactionAccountStatementGroup(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")

    def create_transaction(self, data: Dict[str, Any]) -> TransactionModel:
        """
        Creates a transaction. Available only for admin role and requires request signing.

        The 201 body is the legacy transaction shape (``value`` / ``taxesVat`` /
        ``transactionStatementId`` / ``ref``), NOT a v2.1 transaction -- parsing it as
        ``FinanceTransactionsV21`` raised a ValidationError after the write had already
        landed.

        .. note::
           Sync request signing is broken upstream in the transport
           (``client._make_request_sync`` concatenates the query string without a ``?``
           before signing), so prefer ``create_transaction_async`` until that is fixed.

        Args:
            data: Dict containing transaction data with the following fields:
                seller_id: Seller identifier (required)
                transaction_type_id: Transaction type identifier (required)
                account_statement_group_id: Account statement group identifier (required)
                value: Transaction value (required)
                currency: Transaction currency (required)
                description: Transaction description
                reference_id: Reference identifier
                vat_tax: VAT tax value
                wht_tax: WHT tax value

        Returns:
            The created transaction, in the legacy transaction shape
        """
        url = "/v2/finance/transaction"

        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=data, requires_signing=True)
            return TransactionModel(**response)
        else:
            raise TypeError("This method requires a synchronous client")

    async def create_transaction_async(self, data: Dict[str, Any]) -> TransactionModel:
        """
        Creates a transaction asynchronously. Available only for admin role and requires request signing.

        The 201 body is the legacy transaction shape, not a v2.1 transaction;
        see ``create_transaction``.

        Args:
            data: Dict containing transaction data with required fields
                (see create_transaction method for details)

        Returns:
            The created transaction, in the legacy transaction shape
        """
        url = "/v2/finance/transaction"

        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=data, requires_signing=True)
            return TransactionModel(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def list_variables(self, **params: Union[Dict[str, Any], TransactionVariablesListParamsModel]) -> Dict[str, Any]:
        """
        Returns a list of TRE variables which belongs to Global -> Seller inheritance group.
        This endpoint is only available for the admin role.
        
        Args:
            seller_id: The ID of the seller
            seller_src_id: External ID of the seller from third party service
            variable_name: Exact name of TRE variable
            variable_value: Exact value of TRE variable
            limit: Maximum number of items to return
            offset: Offset for pagination
            
        Returns:
            Dict containing variables and pagination info
        """
        url = "/v2/finance/variables"

        params = TransactionVariablesListParamsModel(**params).model_dump(exclude_none=True)

        if hasattr(self._client, '_make_request_sync'):
            return self._client._make_request_sync("GET", url, params=params)
        else:
            raise TypeError("This method requires a synchronous client")

    async def list_variables_async(self, **params: Union[Dict[str, Any], TransactionVariablesListParamsModel]) -> Dict[str, Any]:
        """
        Returns a list of TRE variables asynchronously.

        Args:
            See list_variables method for available parameters

        Returns:
            Dict containing variables and pagination info
        """
        url = "/v2/finance/variables"

        # ``**params`` always arrives as a plain dict, so the old
        # ``isinstance(params, TransactionVariablesListParamsModel)`` branch never fired
        # and the async twin sent raw snake_case keys where the sync one sent validated
        # ones. Validate unconditionally, exactly as the sync twin does.
        params = TransactionVariablesListParamsModel(**params).model_dump(exclude_none=True)

        if hasattr(self._client, '_make_request_async'):
            return await self._client._make_request_async("GET", url, params=params)
        else:
            raise TypeError("This method requires an asynchronous client")
