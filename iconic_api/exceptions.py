# -*- coding: utf-8 -*-
import httpx
from typing import Optional, Any, Dict

class IconicAPIError(Exception):
    """Base exception for Iconic API client errors."""
    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message)
        self.status_code = response.status_code
        self.response_content = response.content
        self.request_url = response.request.url
        self.request_method = response.request.method
        self.request_url = response.request.url
        self.request_params = response.request.url.params
        self.request_data = response.request.content
        self.response_headers = response.headers
        
        try:
            self.response_json = response.json()
        except Exception:
            self.response_json = None
        
        self.retry_after = None
        if self.response_headers.get('Retry-After'):
            self.retry_after = int(self.response_headers['Retry-After'])

    def __str__(self):
        parts = [super().__str__()]
        if self.status_code:
            parts.append(f"Status Code: {self.status_code}")
        if self.request_method and self.request_url:
            parts.append(f"Request: {self.request_method} {self.request_url}")
        if self.response_json:
            parts.append(f"Response JSON: {self.response_json}")
        elif self.response_content:
            parts.append(f"Response Content: {self.response_content[:500]}") # Truncate for readability
        if hasattr(self, 'retry_after'):
            parts.append(f"Retry After: {self.retry_after}")
        return "\n".join(parts)

class AuthenticationError(IconicAPIError):
    """Raised for authentication failures."""
    pass

class RateLimitError(IconicAPIError):
    """Raised when API rate limits are exceeded."""
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

class MaintenanceModeError(IconicAPIError):
    """Raised when the API is in maintenance mode (503)."""
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after