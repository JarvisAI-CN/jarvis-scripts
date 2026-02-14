"""
API mocking examples for testing external services.
"""

import asyncio
from e2e_test_framework import (
    TestCase,
    test_case,
    expect,
    HttpMock,
    ApiMock,
    mock_api_response,
    mock_api_error,
    mock_sequence,
    mock_conditional
)


@test_case(name="HTTP GET Mocking", tags=["api", "mock"])
class TestHTTPGetMocking(TestCase):
    """Test HTTP GET request mocking."""
    
    async def execute_test(self):
        # Create HTTP mock
        api = HttpMock(base_url="https://api.example.com")
        
        # Mock GET /users
        api.get("/users", {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ]
        })
        
        # Execute request
        response = api.request("GET", "/users")
        
        # Verify response
        expect(response.status_code).to_eq(200)
        expect(response.body["users"]).to_have_length(2)
        expect(response.body["users"][0]["name"]).to_eq("Alice")
        
        # Verify request was captured
        requests = api.get_requests(method="GET")
        expect(requests).to_have_length(1)
        expect(requests[0].url).to_contain("/users")


@test_case(name="HTTP POST Mocking", tags=["api", "mock"])
class TestHTTPPOSTMocking(TestCase):
    """Test HTTP POST request mocking."""
    
    async def execute_test(self):
        api = HttpMock()
        
        # Mock POST /login
        def login_handler(request):
            email = request.body.get("email")
            password = request.body.get("password")
            
            if email == "user@example.com" and password == "password123":
                from e2e_test_framework import MockResponse
                return MockResponse(
                    status_code=200,
                    body={"token": "abc123", "user_id": 1}
                )
            else:
                from e2e_test_framework import MockResponse
                return MockResponse(
                    status_code=401,
                    body={"error": "Invalid credentials"}
                )
        
        api.add_handler("POST", "/login", login_handler)
        
        # Test successful login
        response = api.request("POST", "/login", body={
            "email": "user@example.com",
            "password": "password123"
        })
        
        expect(response.status_code).to_eq(200)
        expect(response.body["token"]).to_eq("abc123")
        
        # Test failed login
        response = api.request("POST", "/login", body={
            "email": "user@example.com",
            "password": "wrong"
        })
        
        expect(response.status_code).to_eq(401)
        expect(response.body["error"]).to_contain("Invalid")


@test_case(name="RESTful Resource Mocking", tags=["api", "mock"])
class TestRESTfulResource(TestCase):
    """Test RESTful resource CRUD mocking."""
    
    async def execute_test(self):
        api = ApiMock(base_path="/api/v1")
        
        # Mock full CRUD for users resource
        api.resource("users").with_crud([
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ])
        
        # GET /users - List all
        response = api.request("GET", "/users")
        expect(response.status_code).to_eq(200)
        expect(response.body).to_have_length(2)
        
        # GET /users/1 - Get single
        response = api.request("GET", "/users/1")
        expect(response.status_code).to_eq(200)
        expect(response.body["name"]).to_eq("Alice")
        
        # POST /users - Create
        response = api.request("POST", "/users", body={
            "name": "Charlie",
            "email": "charlie@example.com"
        })
        expect(response.status_code).to_eq(201)
        expect(response.body["id"]).to_eq(3)
        
        # PUT /users/1 - Update
        response = api.request("PUT", "/users/1", body={
            "name": "Alice Updated"
        })
        expect(response.status_code).to_eq(200)
        expect(response.body["name"]).to_eq("Alice Updated")
        
        # DELETE /users/2 - Delete
        response = api.request("DELETE", "/users/2")
        expect(response.status_code).to_eq(204)
        
        # Verify deletion
        response = api.request("GET", "/users/2")
        expect(response.status_code).to_eq(404)


@test_case(name="Sequence Mocking", tags=["api", "mock", "advanced"])
class TestSequenceMocking(TestCase):
    """Test sequential response mocking."""
    
    async def execute_test(self):
        api = HttpMock()
        
        # Mock multiple responses in sequence
        from e2e_test_framework import MockResponse, mock_sequence
        
        api.get("/status", mock_sequence(
            MockResponse(status_code=200, body={"status": "pending"}),
            MockResponse(status_code=200, body={"status": "processing"}),
            MockResponse(status_code=200, body={"status": "completed"})
        ))
        
        # First call - pending
        r1 = api.request("GET", "/status")
        expect(r1.body["status"]).to_eq("pending")
        
        # Second call - processing
        r2 = api.request("GET", "/status")
        expect(r2.body["status"]).to_eq("processing")
        
        # Third call - completed
        r3 = api.request("GET", "/status")
        expect(r3.body["status"]).to_eq("completed")
        
        # Fourth call - returns last response
        r4 = api.request("GET", "/status")
        expect(r4.body["status"]).to_eq("completed")


@test_case(name="Conditional Mocking", tags=["api", "mock", "advanced"])
class TestConditionalMocking(TestCase):
    """Test conditional response mocking."""
    
    async def execute_test(self):
        api = HttpMock()
        
        # Mock based on request condition
        def is_admin(request):
            return request.headers.get("X-Role") == "admin"
        
        from e2e_test_framework import mock_conditional
        api.get("/admin/users", mock_conditional(
            condition=is_admin,
            true_response={"users": ["all users"]},
            false_response={"error": "Unauthorized"}
        ))
        
        # Admin request
        response = api.request("GET", "/admin/users", headers={
            "X-Role": "admin"
        })
        expect(response.status_code).to_eq(200)
        expect(response.body).to_have_key("users")
        
        # Non-admin request
        response = api.request("GET", "/admin/users", headers={
            "X-Role": "user"
        })
        expect(response.status_code).to_eq(404)
        expect(response.body["error"]).to_contain("Unauthorized")


@test_case(name="Error Simulation", tags=["api", "mock"])
class TestErrorSimulation(TestCase):
    """Test API error simulation."""
    
    async def execute_test(self):
        api = HttpMock()
        
        # Mock 500 error
        api.get("/error", status_code=500, body={"error": "Internal server error"})
        
        response = api.request("GET", "/error")
        expect(response.status_code).to_eq(500)
        expect(response.body["error"]).to_contain("Internal")
        
        # Mock network delay
        api.get("/slow", {"data": "response"}, delay=0.5)
        
        import time
        start = time.time()
        response = api.request("GET", "/slow")
        duration = time.time() - start
        
        expect(response.status_code).to_eq(200)
        expect(duration).to_be_gte(0.4)  # Account for timing variance


@test_case(name="Request Verification", tags=["api", "mock"])
class TestRequestVerification(TestCase):
    """Test request capturing and verification."""
    
    async def execute_test(self):
        api = HttpMock()
        api.post("/api/track", {"tracked": True})
        
        # Make multiple requests
        for i in range(3):
            api.request("POST", "/api/track", body={"event": f"action_{i}"})
        
        # Verify all requests were captured
        requests = api.get_requests(method="POST")
        expect(requests).to_have_length(3)
        
        # Verify request details
        expect(requests[0].body["event"]).to_eq("action_0")
        expect(requests[1].body["event"]).to_eq("action_1")
        expect(requests[2].body["event"]).to_eq("action_2")
        
        # Filter by path
        track_requests = api.get_requests(path="/api/track")
        expect(track_requests).to_have_length(3)


@test_case(name="API Integration Test", tags=["api", "integration"])
class TestAPIIntegration(TestCase):
    """Simulate real API integration test."""
    
    async def execute_test(self):
        # Setup mock API
        api = ApiMock()
        
        # Mock authentication
        api.resource("auth")
           .post("login", {"token": "jwt_token", "user_id": 1})
        
        # Mock user resource
        api.resource("users").with_crud([
            {"id": 1, "name": "Alice", "email": "alice@example.com"}
        ])
        
        # Simulate user flow
        # 1. Login
        login_resp = api.request("POST", "/auth/login", body={
            "email": "alice@example.com",
            "password": "password"
        })
        expect(login_resp.status_code).to_eq(201)
        token = login_resp.body["token"]
        expect(token).to_eq("jwt_token")
        
        # 2. Get user profile
        user_resp = api.request("GET", "/users/1")
        expect(user_resp.status_code).to_eq(200)
        expect(user_resp.body["name"]).to_eq("Alice")
        
        # 3. Update user
        update_resp = api.request("PUT", "/users/1", body={
            "name": "Alice Updated"
        })
        expect(update_resp.status_code).to_eq(200)
        
        # 4. Verify update
        verify_resp = api.request("GET", "/users/1")
        expect(verify_resp.body["name"]).to_eq("Alice Updated")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/ubuntu/.openclaw/workspace")
    
    from e2e_test_framework import create_suite, generate_html_report
    
    suite = create_suite("API Mocking Tests")
    suite.add_tests(
        TestHTTPGetMocking,
        TestHTTPPOSTMocking,
        TestRESTfulResource,
        TestSequenceMocking,
        TestConditionalMocking,
        TestErrorSimulation,
        TestRequestVerification,
        TestAPIIntegration
    )
    
    async def main():
        summary = await suite.run(
            parallel=2,
            filter_tags=["api"],
            verbose=True
        )
        
        report_path = generate_html_report(summary, "api_mock_report.html")
        print(f"\n📄 Report: {report_path}")
    
    asyncio.run(main())
