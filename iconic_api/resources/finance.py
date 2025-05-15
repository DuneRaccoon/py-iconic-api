from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .base import IconicResource
from ..models import (
    FinanceStatement,
    FinanceStatementListParamsModel,
    FinanceStatementDetails
)

class Finance(IconicResource):
    """
    Finance resource for managing financial statements and related data.
    
    Provides methods for accessing finance statements, their details, and more.
    """
    
    endpoint = "finance"
    model_class = None  # No specific model for the resource itself
    
    def list_statements(self, **params: Union[Dict[str, Any], FinanceStatementListParamsModel]) -> List[FinanceStatement]:
        """
        Get a list of finance statements based on specified parameters.
        
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

    async def list_statements_async(self, **params: Union[Dict[str, Any], FinanceStatementListParamsModel]) -> List[FinanceStatement]:
        """
        Get a list of finance statements based on specified parameters, asynchronously.
        
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
            
    def get_current_statement(self, country: str, statement_type: str = "marketplace") -> FinanceStatement:
        """
        Get a current finance statement for a specific country.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            The current finance statement
        """
        url = f"/v2/finance/statements/current/{country}"
        params = {"type": statement_type}
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return FinanceStatement(**response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_current_statement_async(self, country: str, statement_type: str = "marketplace") -> FinanceStatement:
        """
        Get a current finance statement for a specific country, asynchronously.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            The current finance statement
        """
        url = f"/v2/finance/statements/current/{country}"
        params = {"type": statement_type}
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return FinanceStatement(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_current_statement_details(self, country: str, statement_type: str = "marketplace") -> FinanceStatementDetails:
        """
        Get details of the current finance statement for a specific country.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            The current finance statement details
        """
        url = f"/v2/finance/statements/current/{country}/details"
        params = {"type": statement_type}
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return FinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_current_statement_details_async(self, country: str, statement_type: str = "marketplace") -> FinanceStatementDetails:
        """
        Get details of the current finance statement for a specific country, asynchronously.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            The current finance statement details
        """
        url = f"/v2/finance/statements/current/{country}/details"
        params = {"type": statement_type}
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return FinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
