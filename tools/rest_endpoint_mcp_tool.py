"""
REST Endpoint MCP Tool implementation
"""
import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlencode
from .base_mcp_tool import BaseMCPTool


class RESTEndpointMCPTool(BaseMCPTool):
    """MCP Tool for REST API endpoint operations"""

    def _initialize(self):
        """Initialize REST endpoint specific components"""
        self.default_timeout = 30
        self.session = requests.Session()

        # Load authentication configuration if provided
        self.auth_config = self.config.get('authentication', {})
        self._setup_authentication()

    def _setup_authentication(self):
        """Setup authentication based on configuration"""
        auth_type = self.auth_config.get('type', 'none')

        if auth_type == 'basic':
            username = self.auth_config.get('username', '')
            password = self.auth_config.get('password', '')
            self.session.auth = (username, password)

        elif auth_type == 'bearer':
            token = self.auth_config.get('token', '')
            self.session.headers.update({'Authorization': f'Bearer {token}'})

        elif auth_type == 'api_key':
            key = self.auth_config.get('key', '')
            header_name = self.auth_config.get('header_name', 'X-API-Key')
            self.session.headers.update({header_name: key})

        elif auth_type == 'custom':
            headers = self.auth_config.get('headers', {})
            self.session.headers.update(headers)

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle REST endpoint tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "get_request": self._get_request,
                "post_request": self._post_request,
                "put_request": self._put_request,
                "delete_request": self._delete_request,
                "patch_request": self._patch_request,
                "custom_request": self._custom_request,
                "test_endpoint": self._test_endpoint,
                "get_endpoint_info": self._get_endpoint_info
            }

            if tool_name in tool_methods:
                result = tool_methods[tool_name](arguments)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            self.record_call(tool_name, arguments, result=result)
            return result

        except Exception as e:
            error_msg = str(e)
            self.record_call(tool_name, arguments, error=error_msg)
            return {"error": error_msg, "status": 500}

    def _build_url(self, base_url: str, path: str = "", query_params: Optional[Dict] = None) -> str:
        """Build complete URL with query parameters"""
        url = urljoin(base_url, path) if path else base_url

        if query_params:
            query_string = urlencode(query_params)
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}{query_string}"

        return url

    def _prepare_headers(self, custom_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Prepare request headers"""
        headers = dict(self.session.headers)

        if custom_headers:
            headers.update(custom_headers)

        # Ensure Content-Type is set for JSON requests
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        return headers

    def _make_request(
            self,
            method: str,
            url: str,
            data: Optional[Dict] = None,
            headers: Optional[Dict] = None,
            timeout: Optional[int] = None,
            auth: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """Make HTTP request and return formatted response"""
        try:
            timeout = timeout or self.default_timeout

            request_kwargs = {
                'timeout': timeout,
                'headers': headers or {}
            }

            if auth:
                request_kwargs['auth'] = auth

            if data and method.upper() in ['POST', 'PUT', 'PATCH']:
                request_kwargs['json'] = data

            response = self.session.request(method, url, **request_kwargs)

            # Try to parse JSON response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text

            return {
                "status_code": response.status_code,
                "success": response.ok,
                "data": response_data,
                "headers": dict(response.headers),
                "url": response.url,
                "elapsed_ms": response.elapsed.total_seconds() * 1000
            }

        except requests.exceptions.Timeout:
            return {
                "error": "Request timeout",
                "status_code": 408,
                "success": False
            }
        except requests.exceptions.ConnectionError:
            return {
                "error": "Connection error",
                "status_code": 503,
                "success": False
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status_code": 500,
                "success": False
            }

    def _get_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GET request"""
        url = params.get('url', '')
        query_params = params.get('query_params', {})
        headers = params.get('headers', {})
        timeout = params.get('timeout')

        if not url:
            return {"error": "URL is required"}

        full_url = self._build_url(url, query_params=query_params)
        prepared_headers = self._prepare_headers(headers)

        return self._make_request('GET', full_url, headers=prepared_headers, timeout=timeout)

    def _post_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute POST request"""
        url = params.get('url', '')
        data = params.get('data', {})
        query_params = params.get('query_params', {})
        headers = params.get('headers', {})
        timeout = params.get('timeout')

        if not url:
            return {"error": "URL is required"}

        full_url = self._build_url(url, query_params=query_params)
        prepared_headers = self._prepare_headers(headers)

        return self._make_request('POST', full_url, data=data, headers=prepared_headers, timeout=timeout)

    def _put_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PUT request"""
        url = params.get('url', '')
        data = params.get('data', {})
        query_params = params.get('query_params', {})
        headers = params.get('headers', {})
        timeout = params.get('timeout')

        if not url:
            return {"error": "URL is required"}

        full_url = self._build_url(url, query_params=query_params)
        prepared_headers = self._prepare_headers(headers)

        return self._make_request('PUT', full_url, data=data, headers=prepared_headers, timeout=timeout)

    def _delete_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DELETE request"""
        url = params.get('url', '')
        query_params = params.get('query_params', {})
        headers = params.get('headers', {})
        timeout = params.get('timeout')

        if not url:
            return {"error": "URL is required"}

        full_url = self._build_url(url, query_params=query_params)
        prepared_headers = self._prepare_headers(headers)

        return self._make_request('DELETE', full_url, headers=prepared_headers, timeout=timeout)

    def _patch_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PATCH request"""
        url = params.get('url', '')
        data = params.get('data', {})
        query_params = params.get('query_params', {})
        headers = params.get('headers', {})
        timeout = params.get('timeout')

        if not url:
            return {"error": "URL is required"}

        full_url = self._build_url(url, query_params=query_params)
        prepared_headers = self._prepare_headers(headers)

        return self._make_request('PATCH', full_url, data=data, headers=prepared_headers, timeout=timeout)

    def _custom_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom HTTP request with full control"""
        url = params.get('url', '')
        method = params.get('method', 'GET').upper()
        data = params.get('data', {})
        query_params = params.get('query_params', {})
        headers = params.get('headers', {})
        timeout = params.get('timeout')
        auth_override = params.get('auth')  # Tuple of (username, password)

        if not url:
            return {"error": "URL is required"}

        if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
            return {"error": f"Unsupported HTTP method: {method}"}

        full_url = self._build_url(url, query_params=query_params)
        prepared_headers = self._prepare_headers(headers)

        return self._make_request(
            method,
            full_url,
            data=data if method in ['POST', 'PUT', 'PATCH'] else None,
            headers=prepared_headers,
            timeout=timeout,
            auth=auth_override
        )

    def _test_endpoint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test endpoint connectivity and response"""
        url = params.get('url', '')

        if not url:
            return {"error": "URL is required"}

        try:
            # Simple HEAD request to test connectivity
            response = self.session.head(url, timeout=10)

            return {
                "url": url,
                "reachable": True,
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "headers": dict(response.headers)
            }
        except Exception as e:
            return {
                "url": url,
                "reachable": False,
                "error": str(e)
            }

    def _get_endpoint_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about configured endpoints"""
        return {
            "authentication_type": self.auth_config.get('type', 'none'),
            "default_timeout": self.default_timeout,
            "session_headers": dict(self.session.headers),
            "supported_methods": ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        }