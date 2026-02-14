"""
Basic test examples demonstrating the framework's features.
"""

import asyncio
from e2e_test_framework import (
    TestCase,
    test_case,
    test,
    expect,
    skip,
    retry,
    timeout,
    tags,
    setup,
    teardown,
    setup_class,
    teardown_class,
    apply_hooks
)


# Example 1: Simple test case
@test_case(
    name="Basic Assertions",
    description="Demonstrate basic assertion chains",
    timeout=10,
    tags=["basic", "smoke"]
)
class TestBasicAssertions(TestCase):
    """Test basic assertion functionality."""
    
    async def execute_test(self):
        # Equality
        expect(1 + 1).to_eq(2)
        expect("hello").to_eq("hello")
        
        # Type checks
        expect(42).to_be_type(int)
        expect([1, 2, 3]).to_be_type(list)
        expect(None).to_be_none()
        
        # Numeric comparisons
        expect(10).to_be_gt(5)
        expect(10).to_be_gte(10)
        expect(5).to_be_lt(10)
        expect(5).to_be_lte(5)
        expect(3.14159).to_be_close_to(3.14, tolerance=0.01)
        
        # String assertions
        expect("hello world").to_contain("world")
        expect("hello@example.com").to_match(r"^[a-z]+@[a-z]+\.[a-z]+$")
        expect("prefix_value").to_start_with("prefix")
        expect("value_suffix").to_end_with("suffix")
        
        # Collection assertions
        expect([1, 2, 3]).to_have_length(3)
        expect([1, 2, 3]).to_include(2)
        expect({"a": 1, "b": 2}).to_have_key("a")
        
        # Negations
        expect(5).not_().to_eq(10)
        expect("hello").not_().to_contain("world")
        
        # Callable/exception
        def divide_by_zero():
            return 1 / 0
        
        expect(divide_by_zero).to_throw(ZeroDivisionError)


# Example 2: Async operations
@test_case(name="Async Operations", timeout=15, tags=["async"])
@apply_hooks
class TestAsyncOperations(TestCase):
    """Test async functionality."""
    
    async def setup(self):
        """Setup before test."""
        self.data = []
    
    async def teardown(self):
        """Cleanup after test."""
        self.data.clear()
    
    async def fetch_data(self, delay: float = 0.1) -> dict:
        """Simulate async API call."""
        await asyncio.sleep(delay)
        return {"status": "ok", "data": [1, 2, 3]}
    
    async def execute_test(self):
        # Test async operation
        result = await self.fetch_data(0.1)
        expect(result["status"]).to_eq("ok")
        expect(result["data"]).to_have_length(3)
        
        # Test concurrent operations
        tasks = [self.fetch_data(0.1) for _ in range(3)]
        results = await asyncio.gather(*tasks)
        expect(results).to_have_length(3)


# Example 3: Retry mechanism
@test_case(name="Flaky Test with Retry", retries=3, retry_delay=0.5)
class TestFlaky(TestCase):
    """Demonstrate retry mechanism."""
    
    def __init__(self):
        super().__init__()
        self.attempts = 0
    
    async def execute_test(self):
        self.attempts += 1
        
        # Simulate flaky condition
        if self.attempts < 2:
            raise Exception("Random failure (will retry)")
        
        # Will pass on 2nd attempt
        expect(self.attempts).to_be_gte(2)


# Example 4: Skip conditions
@test_case(name="Skipped Test", tags=["skip"])
@skip("This test is intentionally skipped")
class TestSkipped(TestCase):
    """Demonstrate skip functionality."""
    
    async def execute_test(self):
        expect(True).to_be_true()


# Example 5: Complex object testing
@test_case(name="Complex Object Testing", tags=["advanced"])
class TestComplexObjects(TestCase):
    """Test complex nested structures."""
    
    async def execute_test(self):
        user = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com",
            "roles": ["admin", "user"],
            "profile": {
                "age": 30,
                "city": "NYC"
            }
        }
        
        # Deep equality
        expected = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com",
            "roles": ["admin", "user"],
            "profile": {
                "age": 30,
                "city": "NYC"
            }
        }
        
        expect(user).to_deep_eq(expected)
        
        # Nested checks
        expect(user["profile"]).to_have_key("age")
        expect(user["roles"]).to_include("admin")


# Example 6: Lifecycle hooks
@test_case(name="Lifecycle Hooks Demo", tags=["lifecycle"])
@apply_hooks
class TestLifecycle(TestCase):
    """Demonstrate test lifecycle."""
    
    shared_data = None
    
    async def setup(self):
        """Setup before each test."""
        self.test_data = []
        self.execution_order.append("setup")
    
    async def teardown(self):
        """Teardown after each test."""
        self.test_data.clear()
        self.execution_order.append("teardown")
    
    @staticmethod
    @setup_class
    def setup_class_method():
        """Setup once before all tests."""
        TestLifecycle.shared_data = "class-level"
        TestLifecycle.execution_order = ["setup_class"]
    
    @staticmethod
    @teardown_class
    def teardown_class_method():
        """Teardown once after all tests."""
        TestLifecycle.shared_data = None
        TestLifecycle.execution_order.append("teardown_class")
    
    async def execute_test(self):
        self.execution_order.append("execute_test")
        
        expect(self.shared_data).to_eq("class-level")
        expect(self.execution_order).to_eq([
            "setup_class", "setup", "execute_test"
        ])


# Example 7: Function-based test using @test decorator
@test(
    name="User Login Test",
    description="Test user authentication flow",
    timeout=5,
    tags=["auth", "smoke"]
)
async def test_user_login(self):
    """Function-based test example."""
    # Simulate login
    user = {
        "email": "user@example.com",
        "password": "secret123"
    }
    
    # Validate input
    expect(user["email"]).to_match(r"^[a-z]+@[a-z]+\.[a-z]+$")
    expect(user["password"]).to_have_length(8)
    
    # Simulate auth response
    auth_response = {
        "success": True,
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "user": {"id": 1, "email": user["email"]}
    }
    
    expect(auth_response["success"]).to_be_true()
    expect(auth_response["token"]).to_start_with("eyJ")
    expect(auth_response["user"]).to_have_key("id")


# Example 8: Parallel execution demo
@test_case(name="Test 1", priority=1, tags=["parallel"])
class TestParallel1(TestCase):
    async def execute_test(self):
        await asyncio.sleep(0.1)
        expect(True).to_be_true()


@test_case(name="Test 2", priority=2, tags=["parallel"])
class TestParallel2(TestCase):
    async def execute_test(self):
        await asyncio.sleep(0.1)
        expect(True).to_be_true()


@test_case(name="Test 3", priority=3, tags=["parallel"])
class TestParallel3(TestCase):
    async def execute_test(self):
        await asyncio.sleep(0.1)
        expect(True).to_be_true()


if __name__ == "__main__":
    # Run examples
    import sys
    sys.path.insert(0, "/home/ubuntu/.openclaw/workspace")
    
    from e2e_test_framework import run_tests, create_suite
    
    # Create suite
    suite = create_suite("Example Tests")
    suite.add_tests(
        TestBasicAssertions,
        TestAsyncOperations,
        TestFlaky,
        TestSkipped,
        TestComplexObjects,
        TestLifecycle,
        TestParallel1,
        TestParallel2,
        TestParallel3
    )
    
    # Run with parallel execution
    import asyncio
    
    async def main():
        summary = await suite.run(
            parallel=3,
            filter_tags=["smoke", "async", "lifecycle", "parallel"],
            verbose=True
        )
        
        # Generate HTML report
        from e2e_test_framework import generate_html_report
        report_path = generate_html_report(summary, "example_report.html")
        print(f"\n📄 HTML report: {report_path}")
    
    asyncio.run(main())
