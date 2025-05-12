from __future__ import annotations

from datetime import date as date_aliased, datetime as datetime_aliased
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from ..models import (
    Order, 
    ShipmentProviderType,
    OrderStatus,
    PackedStatus,
    ShipmentTypes,
    FulfillmentType,
    Customer,
    Provider
)

from ..utils import clean_params

class BaseRequestParamsModel(BaseModel):
    """
    Base model for all request models.
    """
    model_config = ConfigDict(
        allow_extra = "allow",
        allow_population_by_field_name = True,
        use_enum_values = True,
        json_encoders = {
            datetime_aliased: lambda v: v.isoformat() if isinstance(v, datetime_aliased) else v,
            UUID: lambda v: str(v) if isinstance(v, UUID) else v,
        }
    )
    
    limit: int = 100
    offset: int = 0
    
    def to_api_params(self) -> Dict[str, Any]:
        """
        Converts the model instance to a dictionary of API parameters.
        """
        params = self.model_dump(exclude_none=True)
        cleaned_params = clean_params(params)
        return cleaned_params
    
class ListOrdersRequest(BaseRequestParamsModel):
    """
    Request model for listing orders.
    """
    x_context: Optional[Literal["admin", "seller"]] = "seller"
    section: Optional[Union[OrderStatus, ShipmentProviderType]] = None
    date_start: Optional[Union[date_aliased, datetime_aliased]] = None
    date_end: Optional[Union[date_aliased, datetime_aliased]] = None
    order_numbers: Optional[List[str]] = None
    packed: Optional[PackedStatus] = None
    customers: Optional[Customer] = None
    tags: Optional[List[str]] = None
    product_sku: Optional[List[str]] = None
    shipment_type: Optional[ShipmentTypes] = None
    shipment_providers: Optional[List[Provider]] = None
    outlet: bool = False
    invoice_required: bool = False
    cancelation_reasons: List[str] = None
    cancelation_reason_ids: List[int] = None
    fulfilment_type: Optional[FulfillmentType] = None
    order_sources: Optional[List[str]] = None
    seller_names: Optional[List[str]] = None
    seller_ids: Optional[List[int]] = None
    update_date_start: Optional[Union[date_aliased, datetime_aliased]] = None
    update_date_end: Optional[Union[date_aliased, datetime_aliased]] = None
    warehouses: Optional[List[str]] = None
    order_ids: Optional[List[int]] = None
    include_voucher_details: Optional[bool] = None
    sort: Optional[Literal["createdAt", "updatedAt"]] = None
    sort_dir: Optional[Literal["asc", "desc"]] = None
    
    def to_api_params(self) -> Dict[str, Any]:
        if self.section is not None:
            if isinstance(section, OrderStatus):
                section = f"status_{section.value}"
            elif isinstance(section, ShipmentProviderType):
                section = f"group_{section.value}"
        
        if self.customers is not None:
            customers_ = []  
            for customer in self.customers:
                customers_.extend([customer.firstName, customer.lastName])
        
        if self.shipment_providers is not None:
            shipment_providers = [provider.id for provider in self.shipment_providers]
        
        if self.fulfilment_type is not None:
            fulfilment_type = self.fulfilment_type.value
        if self.shipment_type is not None:
            shipment_type = self.shipment_type.value
            
        params = {k: v for k,v in {
            **self.model_dump(exclude_none=True),
            "section": section,
            "customers": customers_,
            "shipment_providers": shipment_providers,
            "fulfilment_type": fulfilment_type,
            "shipment_type": shipment_type,
        }.items() if k != 'x_context'}
        cleaned_params = clean_params(params)
        return cleaned_params
            