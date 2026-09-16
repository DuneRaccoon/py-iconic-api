# -*- coding: utf-8 -*-
"""Models for ``GET /v2/orders/search``.

This endpoint does **not** return orders. It answers with autocomplete suggestions for
a type-ahead box: a ``label`` to display, a ``value`` to feed back into an order filter,
and - for product searches - a ``sublabel`` carrying the product name. Use
``orders.list_orders()`` to fetch the orders themselves.

The allowed values below come from the API's own validation errors, which enumerate the
accepted choices, rather than from the published documentation. The documentation is
wrong in three places, all verified against the live API:

* it names the source key ``order_source``; the API accepts ``source`` and rejects
  ``order_source`` with a 400,
* it omits ``group_kpi_rejection_rate`` and ``group_kpi_return_rate``,
* it describes ``filteredStatus`` as defaulting to ``status_pending``; omitting it in
  fact searches across every status.

``key`` and ``query`` are both mandatory: the API answers a request missing either with
a **500**, not a validation error, so ``SearchOrdersRequest`` refuses to build one.
"""
from enum import StrEnum
from typing import List, Optional

from pydantic import Field

from ._response_base import IconicResponseModel


class OrderSearchKey(StrEnum):
    """What the ``query`` is matched against."""

    ORDER_NUMBER = "order_nr"
    SOURCE = "source"
    CUSTOMER = "customer"
    PRODUCT = "product"
    CANCELATION_REASON = "cancelation-reason"


class OrderSearchFilteredStatus(StrEnum):
    """Optional status or shipment-group restriction on the suggestions."""

    # Order statuses
    SHIPPED = "status_shipped"
    DELIVERED = "status_delivered"
    FAILED = "status_failed"
    RETURNED = "status_returned"
    CANCELED = "status_canceled"
    PENDING = "status_pending"
    PENDING_ALL = "status_pending_all"
    READY_TO_SHIP = "status_ready_to_ship"
    PAYMENT_PENDING = "status_payment_pending"
    SHIPMENT_INFORMATION_PENDING = "status_shipment_information_pending"
    RETURN_SHIPPED_BY_CUSTOMER = "status_return_shipped_by_customer"
    RETURN_WAITING_FOR_APPROVAL = "status_return_waiting_for_approval"
    RETURN_REJECTED = "status_return_rejected"
    RETURN_DELIVERED = "status_return_delivered"
    # Shipment and reporting groups
    GROUP_ECONOMY = "group_economy"
    GROUP_EXPRESS = "group_express"
    GROUP_STANDARD = "group_standard"
    GROUP_DIGITAL = "group_digital"
    GROUP_SAMEDAY = "group_sameday"
    GROUP_AIR = "group_air"
    GROUP_SURFACE = "group_surface"
    GROUP_MISSING_EXTERNAL_INVOICE_ACCESS_KEY = "group_missing_external_invoice_access_key"
    GROUP_KPI_REJECTION_RATE = "group_kpi_rejection_rate"
    GROUP_KPI_RETURN_RATE = "group_kpi_return_rate"
    GROUP_READY_TO_SHIP_MANIFESTED = "group_ready_to_ship_manifested"
    GROUP_READY_TO_SHIP_NONMANIFESTED = "group_ready_to_ship_nonmanifested"


class OrderSearchResult(IconicResponseModel):
    """One autocomplete suggestion.

    ``value`` is nullable in practice - the ``cancelation-reason`` key returns a
    "No reason" row whose value is ``null`` - so nothing here is required.
    """

    label: Optional[str] = Field(None, description="Text to display in the suggestion list")
    value: Optional[str] = Field(
        None, description="Value to send back as an order filter; null for some cancelation reasons"
    )
    sublabel: Optional[str] = Field(
        None, description="Secondary text; the product name when searching by product"
    )


class OrderSearchResponse(IconicResponseModel):
    """The ``{"results": [...]}`` envelope the endpoint answers with."""

    results: List[OrderSearchResult] = Field(default_factory=list)
