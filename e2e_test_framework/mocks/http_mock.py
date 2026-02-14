"""
HTTP request mocking for API testing.
"""

from typing import Dict, Any, Callable, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class MockRequest:
    """Captured HTTP request."""
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    query_params: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "query_params": self.query_params,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class MockResponse:
    """Mock HTTP response."""
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    delay: float = 0.0  # Simulate network delay
    error: Optional[Exception] = None
    
    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "status_code": self.status_code,
            "headers": self.headers,
            "body": self.body,
            "delay": self.delay,
            "error": str(self.error) if self.error else None
        }


class HttpMock:
    """
    HTTP request mock.
    
    Example:
        mock = HttpMock()
        mock.get("/api/users", {"users": [{"id": 1, "name": "Alice"}]})
        mock.post("/api/login", {"token": "abc123"})
        
        # Use in test
        response = mock.request("GET", "/api/users")
        expect(response["status_code"]).to_eq(200)
        expect(response["body"]["users"]).to_have_length(1)
    """
    
    def __init__(self, base_url: str = "https://api.example.com"):
        self.base_url = base_url
        self._handlers: Dict[Tuple[str, str], Callable] = {}
        self._requests: List[MockRequest] = []
        self._default_response = MockResponse(status_code=404, body={"error": "Not mocked"})
    
    def get(self, path: str, response: Any = None, status_code: int = 200, **kwargs):
        """Mock GET request."""
        return self._add_handler("GET", path, response, status_code, **kwargs)
    
    def post(self, path: str, response: Any = None, status_code: int = 201, **kwargs):
        """Mock POST request."""
        return self._add_handler("POST", path, response, status_code, **kwargs)
    
    def put(self, path: str, response: Any = None, status_code: int = 200, **kwargs):
        """Mock PUT request."""
        return self._add_handler("PUT", path, response, status_code, **kwargs)
    
    def delete(self, path: str, response: Any = None, status_code: int = 204, **kwargs):
        """Mock DELETE request."""
        return self._add_handler("DELETE", path, response, status_code, **kwargs)
    
    def patch(self, path: str, response: Any = None, status_code: int = 200, **kwargs):
        """Mock PATCH request."""
        return self._add_handler("PATCH", path, response, status_code, **kwargs)
    
    def _add_handler(
        self,
        method: str,
        path: str,
        response: Any = None,
        status_code: int = 200,
        delay: float = 0.0,
        error: Exception = None
    ):
        """Add route handler."""
        def handler(request: MockRequest):
            mock_response = MockResponse(
                status_code=status_code,
                body=response,
                delay=delay,
                error=error
            )
            return mock_response
        
        self._handlers[(method.upper(), path)] = handler
        return self
    
    def add_handler(self, method: str, path: str, handler: Callable[[MockRequest], MockResponse]):
        """Add custom handler function."""
        self._handlers[(method.upper(), path)] = handler
    
    def request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str] = None,
        body: Any = None,
        query_params: Dict[str, str] = None
    ) -> MockResponse:
        """Execute mocked request."""
        # Capture request
        request = MockRequest(
            method=method.upper(),
            url=self.base_url + path,
            headers=headers or {},
            body=body,
            query_params=query_params or {}
        )
        self._requests.append(request)
        
        # Find handler
        handler = self._handlers.get((method.upper(), path))
        
        if handler is None:
            # Try pattern matching
            for (m, p), h in self._handlers.items():
                if m == method.upper() and self._match_path(p, path):
                    handler = h
                    break
        
        if handler is None:
            return self._default_response
        
        # Execute handler
        response = handler(request)
        
        return response
    
    def _match_path(self, pattern: str, actual: str) -> bool:
        """Match path with wildcards."""
        # Simple wildcard matching (*)
        import re
        pattern_regex = pattern.replace("*", ".*")
        pattern_regex = "^" + pattern_regex + "$"
        return re.match(pattern_regex, actual) is not None
    
    def get_requests(
        self,
        method: str = None,
        path: str = None
    ) -> List[MockRequest]:
        """Get captured requests."""
        filtered = self._requests
        
        if method:
            filtered = [r for r in filtered if r.method == method.upper()]
        
        if path:
            filtered = [r for r in filtered if path in r.url]
        
        return filtered
    
    def clear(self):
        """Clear all captured requests."""
        self._requests.clear()
    
    def reset(self):
        """Reset all handlers."""
        self._handlers.clear()
        self._requests.clear()


class ApiMock:
    """
    High-level API mocking helper.
    
    Example:
        api = ApiMock()
        
        # Chain API definitions
        api.resource("users")
           .list([{"id": 1, "name": "Alice"}])
           .get(1, {"id": 1, "name": "Alice"})
           .create({"id": 2, "name": "Bob"}, status=201)
        
        # Use in tests
        response = api.request("GET", "/users/1")
        expect(response["body"]["name"]).to_eq("Alice")
    """
    
    def __init__(self, base_path: str = "/api"):
        self.http = HttpMock(base_url=f"https://api.example.com{base_path}")
        self.resources: Dict[str, 'ResourceMock'] = {}
    
    def resource(self, name: str) -> 'ResourceMock':
        """Get or create resource mock."""
        if name not in self.resources:
            self.resources[name] = ResourceMock(name, self.http)
        return self.resources[name]
    
    def request(self, method: str, path: str, **kwargs) -> MockResponse:
        """Make request through HTTP mock."""
        return self.http.request(method, path, **kwargs)
    
    def get_requests(self, **kwargs) -> List[MockRequest]:
        """Get all captured requests."""
        return self.http.get_requests(**kwargs)
    
    def clear(self):
        """Clear all requests."""
        self.http.clear()


class ResourceMock:
    """REST resource mocking."""
    
    def __init__(self, name: str, http: HttpMock):
        self.name = name
        self.http = http
        self.base_path = f"/{name}"
        self._items: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
    
    def list(self, items: List[Dict[str, Any]] = None, **kwargs):
        """Mock GET /resource"""
        self.http.get(self.base_path, items or [], **kwargs)
        return self
    
    def get(self, item_id: int, data: Dict[str, Any] = None, **kwargs):
        """Mock GET /resource/:id"""
        path = f"{self.base_path}/{item_id}"
        self.http.get(path, data or {}, **kwargs)
        return self
    
    def create(self, data: Dict[str, Any], **kwargs):
        """Mock POST /resource"""
        self.http.post(self.base_path, data, **kwargs)
        return self
    
    def update(self, item_id: int, data: Dict[str, Any], **kwargs):
        """Mock PUT /resource/:id"""
        path = f"{self.base_path}/{item_id}"
        self.http.put(path, data, **kwargs)
        return self
    
    def delete(self, item_id: int, **kwargs):
        """Mock DELETE /resource/:id"""
        path = f"{self.base_path}/{item_id}"
        self.http.delete(path, **kwargs)
        return self
    
    def with_crud(self, items: List[Dict[str, Any]] = None):
        """Mock full CRUD operations."""
        items = items or []
        
        def list_handler(request):
            return MockResponse(status_code=200, body=list(self._items.values()))
        
        def get_handler(request):
            item_id = int(request.url.split("/")[-1])
            if item_id not in self._items:
                return MockResponse(status_code=404, body={"error": "Not found"})
            return MockResponse(status_code=200, body=self._items[item_id])
        
        def create_handler(request):
            data = request.body
            data["id"] = self._next_id
            self._items[self._next_id] = data
            self._next_id += 1
            return MockResponse(status_code=201, body=data)
        
        def update_handler(request):
            item_id = int(request.url.split("/")[-1])
            if item_id not in self._items:
                return MockResponse(status_code=404, body={"error": "Not found"})
            self._items[item_id].update(request.body)
            return MockResponse(status_code=200, body=self._items[item_id])
        
        def delete_handler(request):
            item_id = int(request.url.split("/")[-1])
            if item_id not in self._items:
                return MockResponse(status_code=404, body={"error": "Not found"})
            del self._items[item_id]
            return MockResponse(status_code=204, body=None)
        
        self.http.add_handler("GET", self.base_path, list_handler)
        self.http.add_handler("GET", f"{self.base_path}/*", get_handler)
        self.http.add_handler("POST", self.base_path, create_handler)
        self.http.add_handler("PUT", f"{self.base_path}/*", update_handler)
        self.http.add_handler("DELETE", f"{self.base_path}/*", delete_handler)
        
        # Pre-populate
        for item in items:
            item["id"] = self._next_id
            self._items[self._next_id] = item
            self._next_id += 1
        
        return self


# Utility functions

def mock_api_response(data: Any, status_code: int = 200):
    """Create mock response."""
    return MockResponse(status_code=status_code, body=data)


def mock_api_error(message: str, status_code: int = 500):
    """Create mock error response."""
    return MockResponse(
        status_code=status_code,
        body={"error": message},
        error=Exception(message)
    )


def mock_sequence(*responses: MockResponse) -> Callable[[MockRequest], MockResponse]:
    """Create handler that returns responses in sequence."""
    def handler(request: MockRequest):
        if not hasattr(handler, "_index"):
            handler._index = 0
        
        if handler._index >= len(responses):
            return responses[-1]
        
        response = responses[handler._index]
        handler._index += 1
        return response
    
    return handler


def mock_conditional(
    condition: Callable[[MockRequest], bool],
    true_response: Any,
    false_response: Any = None
) -> Callable[[MockRequest], MockResponse]:
    """Create conditional handler."""
    def handler(request: MockRequest):
        if condition(request):
            return MockResponse(status_code=200, body=true_response)
        return MockResponse(status_code=404, body=false_response or {"error": "Condition failed"})
    
    return handler
