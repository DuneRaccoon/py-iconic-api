from typing import Dict, Any, List, Optional, Union
from datetime import date, datetime

from .base import IconicResource
from ..models import (
    InvoiceDocumentType,
    InvoiceRequest
)

class Invoice(IconicResource):
    """
    Invoice resource for retrieving and downloading invoice files.
    
    This resource provides methods to access tax documents from external storage
    in zipped format, supporting both individual files and all associated files.
    """
    
    endpoint = "invoices"
    model_class = None  # This endpoint returns binary data, not a structured response
    
    def get_invoice_files(self, 
                        order_numbers: Optional[List[str]] = None,
                        invoice_numbers: Optional[List[str]] = None,
                        po_numbers: Optional[List[str]] = None,
                        document_types: Optional[List[InvoiceDocumentType]] = None,
                        start_date: Optional[Union[date, datetime]] = None,
                        end_date: Optional[Union[date, datetime]] = None) -> bytes:
        """
        Get and download invoice files as a zip archive.
        
        Args:
            order_numbers: List of order numbers to filter by
            invoice_numbers: List of invoice numbers to filter by
            po_numbers: List of purchase order numbers to filter by
            document_types: List of document types to filter by
            start_date: Start date for filtering by creation date
            end_date: End date for filtering by creation date
            
        Returns:
            Binary data containing the zip file with requested documents
        """
        params = {}
        
        if order_numbers:
            params["orderNumbers[]"] = order_numbers
        if invoice_numbers:
            params["invoiceNumbers[]"] = invoice_numbers
        if po_numbers:
            params["poNumbers[]"] = po_numbers
        if document_types:
            # Convert enum values to strings if needed
            doc_type_values = [dt.value if hasattr(dt, 'value') else dt for dt in document_types]
            params["documentTypes[]"] = doc_type_values
        if start_date:
            if isinstance(start_date, datetime):
                params["startDate"] = start_date.date().isoformat()
            else:
                params["startDate"] = start_date.isoformat()
        if end_date:
            if isinstance(end_date, datetime):
                params["endDate"] = end_date.date().isoformat()
            else:
                params["endDate"] = end_date.isoformat()
            
        url = "/v2/invoices"
        
        if hasattr(self._client, '_make_request_sync'):
            # Note: Need to handle binary response differently
            response = self._client._client.get(url, params=params)
            response.raise_for_status()
            return response.content
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_invoice_files_async(self,
                                   order_numbers: Optional[List[str]] = None,
                                   invoice_numbers: Optional[List[str]] = None,
                                   po_numbers: Optional[List[str]] = None,
                                   document_types: Optional[List[InvoiceDocumentType]] = None,
                                   start_date: Optional[Union[date, datetime]] = None,
                                   end_date: Optional[Union[date, datetime]] = None) -> bytes:
        """
        Get and download invoice files as a zip archive asynchronously.
        
        Args:
            order_numbers: List of order numbers to filter by
            invoice_numbers: List of invoice numbers to filter by
            po_numbers: List of purchase order numbers to filter by
            document_types: List of document types to filter by
            start_date: Start date for filtering by creation date
            end_date: End date for filtering by creation date
            
        Returns:
            Binary data containing the zip file with requested documents
        """
        params = {}
        
        if order_numbers:
            params["orderNumbers[]"] = order_numbers
        if invoice_numbers:
            params["invoiceNumbers[]"] = invoice_numbers
        if po_numbers:
            params["poNumbers[]"] = po_numbers
        if document_types:
            # Convert enum values to strings if needed
            doc_type_values = [dt.value if hasattr(dt, 'value') else dt for dt in document_types]
            params["documentTypes[]"] = doc_type_values
        if start_date:
            if isinstance(start_date, datetime):
                params["startDate"] = start_date.date().isoformat()
            else:
                params["startDate"] = start_date.isoformat()
        if end_date:
            if isinstance(end_date, datetime):
                params["endDate"] = end_date.date().isoformat()
            else:
                params["endDate"] = end_date.isoformat()
            
        url = "/v2/invoices"
        
        if hasattr(self._client, '_make_request_async'):
            # Note: Need to handle binary response differently
            response = await self._client._client.get(url, params=params)
            response.raise_for_status()
            return response.content
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_invoice_files_with_model(self, request: InvoiceRequest) -> bytes:
        """
        Get and download invoice files using a request model.
        
        Args:
            request: InvoiceRequest model containing filter parameters
            
        Returns:
            Binary data containing the zip file with requested documents
        """
        return self.get_invoice_files(
            order_numbers=request.order_numbers,
            invoice_numbers=request.invoice_numbers,
            po_numbers=request.po_numbers,
            document_types=request.document_types,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
    async def get_invoice_files_with_model_async(self, request: InvoiceRequest) -> bytes:
        """
        Get and download invoice files using a request model asynchronously.
        
        Args:
            request: InvoiceRequest model containing filter parameters
            
        Returns:
            Binary data containing the zip file with requested documents
        """
        return await self.get_invoice_files_async(
            order_numbers=request.order_numbers,
            invoice_numbers=request.invoice_numbers,
            po_numbers=request.po_numbers,
            document_types=request.document_types,
            start_date=request.start_date,
            end_date=request.end_date
        )
