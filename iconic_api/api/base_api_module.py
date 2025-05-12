from typing import TYPE_CHECKING, Any, Dict, Optional, Union, List

if TYPE_CHECKING:
    from ..client import IconicClient, IconicAsyncClient


class BaseAPIModule:
    def __init__(self, client: Union['IconicClient', 'IconicAsyncClient']):
        self._client = client

    def _prepare_payload(self, payload: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if payload is None:
            return None
        # Convert snake_case keys to camelCase for the API
        # Pydantic models with aliases handle this for response parsing
        # For request payloads, if they are dicts, we might need to convert keys
        return {self._client.utils.to_api_parameter_name(k): v for k, v in payload.items()}

    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._client.utils.clean_params(params)