# E2E Test Framework

A lightweight, extensible end-to-end testing framework for Python with async support, powerful mocking, and beautiful reports.

## Features

- ✅ **Rich Assertion API** - Chainable, readable assertions
- 🚀 **Async Support** - First-class async/await support
- 🔄 **Retry Mechanism** - Built-in retry with configurable delay
- 🎭 **HTTP Mocking** - Mock API responses without external dependencies
- 📊 **Beautiful Reports** - HTML, JSON, JUnit, and Console reports
- 🔌 **Plugin System** - Extensible with custom reporters and hooks
- ⚡ **Parallel Execution** - Run tests concurrently
- 🎯 **Test Filtering** - Filter by tags, names, or custom criteria

## Installation

```bash
# No external dependencies required - pure Python 3.8+
cp -r e2e_test_framework /path/to/your/project
cd /path/to/your/project
export PYTHONPATH="${PYTHONPATH}:/path/to/your/project"
```

## Quick Start

### Basic Test

```python
from e2e_test_framework import TestCase, test_case, expect

@test_case(name="My First Test", timeout=10, tags=["smoke"])
class TestExample(TestCase):
    async def execute_test(self):
        expect(1 + 1).to_eq(2)
        expect("hello").to_contain("ell")
        expect([1, 2, 3]).to_have_length(3)
```

### Running Tests

```python
from e2e_test_framework import run_tests

summary = run_tests(
    [TestExample, TestAnother],
    parallel=2,
    filter_tags=["smoke"],
    verbose=True
)
```

## Assertion API

### Basic Assertions

```python
# Equality
expect(1 + 1).to_eq(2)
expect({"a": 1}).to_deep_eq({"a": 1})

# Type checks
expect(42).to_be_type(int)
expect(None).to_be_none()

# Numeric
expect(10).to_be_gt(5)
expect(10).to_be_gte(10)
expect(3.14).to_be_close_to(3.1, tolerance=0.05)

# String
expect("hello world").to_contain("world")
expect("alice@example.com").to_match(r"^[a-z]+@[a-z]+\.[a-z]+$")

# Collection
expect([1, 2, 3]).to_have_length(3)
expect({"a": 1}).to_have_key("a")

# Negation
expect(5).not_().to_eq(10)
```

### Exception Testing

```python
def divide_by_zero():
    return 1 / 0

expect(divide_by_zero).to_throw(ZeroDivisionError)
```

## Test Decorators

### Test Case Options

```python
@test_case(
    name="User Authentication",
    description="Test login and registration flow",
    timeout=30,
    retries=3,
    tags=["auth", "critical"]
)
class TestAuth(TestCase):
    async def execute_test(self):
        expect(True).to_be_true()
```

### Skip and Retry

```python
@skip("Feature not ready")
class TestFutureFeature(TestCase):
    async def execute_test(self):
        pass

@retry(count=3, delay=1.0)
class TestFlaky(TestCase):
    async def execute_test(self):
        # Will retry up to 3 times on failure
        pass
```

### Function-Based Tests

```python
@test(name="Quick Test", tags=["smoke"])
async def test_something(self):
    expect(1).to_eq(1)
```

## Lifecycle Hooks

```python
@test_case(name="Lifecycle Demo")
@apply_hooks
class TestWithHooks(TestCase):
    
    async def setup(self):
        """Runs before each test"""
        self.data = []
    
    async def teardown(self):
        """Runs after each test"""
        self.data.clear()
    
    @staticmethod
    @setup_class
    def setup_once():
        """Runs once before all tests"""
        pass
    
    @staticmethod
    @teardown_class
    def teardown_once():
        """Runs once after all tests"""
        pass
    
    async def execute_test(self):
        expect(self.data).to_eq([])
```

## API Mocking

### Basic HTTP Mocking

```python
from e2e_test_framework import HttpMock

api = HttpMock(base_url="https://api.example.com")

# Mock GET endpoint
api.get("/users", {
    "users": [
        {"id": 1, "name": "Alice"}
    ]
})

# Use in test
response = api.request("GET", "/users")
expect(response.status_code).to_eq(200)
expect(response.body["users"]).to_have_length(1)
```

### RESTful Resource Mocking

```python
from e2e_test_framework import ApiMock

api = ApiMock()

# Auto-generate CRUD endpoints
api.resource("users").with_crud([
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
])

# GET /users - List all
r1 = api.request("GET", "/users")

# GET /users/1 - Get single
r2 = api.request("GET", "/users/1")

# POST /users - Create
r3 = api.request("POST", "/users", body={"name": "Charlie"})

# PUT /users/1 - Update
r4 = api.request("PUT", "/users/1", body={"name": "Alice Updated"})

# DELETE /users/1 - Delete
r5 = api.request("DELETE", "/users/1")
```

### Custom Handlers

```python
def auth_handler(request):
    if request.body.get("password") == "secret":
        return MockResponse(status_code=200, body={"token": "jwt"})
    return MockResponse(status_code=401, body={"error": "Unauthorized"})

api.post("/login", auth_handler)
```

## Test Suites

```python
from e2e_test_framework import create_suite

suite = create_suite("My Test Suite")

# Add individual tests
suite.add_test(TestAuthentication)
suite.add_test(TestUsers)

# Add multiple at once
suite.add_tests(TestPosts, TestComments)

# Add nested suites
auth_suite = create_suite("Auth Tests")
auth_suite.add_tests(TestLogin, TestRegister)
suite.add_suite(auth_suite)

# Run suite
summary = await suite.run(parallel=3, filter_tags=["smoke"])
```

## Reporters

### HTML Report

```python
from e2e_test_framework import generate_html_report

report_path = generate_html_report(summary, "report.html")
print(f"Report: {report_path}")
```

Features:
- 📊 Visual statistics
- 🔍 Test filtering
- 📈 Progress bars
- ❌ Error details with stack traces
- 📅 Timestamps and durations

### JSON Report

```python
from e2e_test_framework import generate_json_report

json_path = generate_json_report(summary, "report.json")
```

### JUnit XML (CI/CD)

```python
from e2e_test_framework import generate_junit_report

junit_path = generate_junit_report(summary, "junit.xml")
```

### Console Reporter

```python
from e2e_test_framework import ConsoleReporter

reporter = ConsoleReporter(use_colors=True)
runner = TestRunner(reporter=reporter)
```

## Advanced Features

### Parallel Execution

```python
# Run 3 tests concurrently
summary = await suite.run(parallel=3)
```

### Test Filtering

```python
# By tags
summary = await suite.run(filter_tags=["smoke", "critical"])

# By name
summary = await suite.run(filter_names=["TestAuthentication"])

# By priority (higher runs first)
@test_case(priority=10)
class HighPriorityTest(TestCase):
    pass
```

### Dependencies

```python
@test_case(name="Dependent Test")
@depends_on("TestAuthentication", "TestDatabaseSetup")
class TestRequires(TestCase):
    async def execute_test(self):
        # Only runs if dependencies pass
        pass
```

### Custom Hooks

```python
runner = TestRunner()

@runner.add_hook('before_test')
async def log_test_start(info):
    print(f"Starting: {info.name}")

@runner.add_hook('on_error')
async def notify_failure(info, result, error):
    send_slack_notification(f"Test failed: {info.name}")
```

## Project Structure

```
e2e_test_framework/
├── core/
│   ├── assertions.py      # Assertion library
│   ├── case.py           # Test case base
│   └── runner.py         # Test runner
├── mocks/
│   └── http_mock.py      # HTTP API mocking
├── reporters/
│   ├── console_reporter.py
│   ├── html_reporter.py
│   └── json_reporter.py
├── examples/
│   ├── test_basic.py
│   └── test_api_mocking.py
└── __init__.py
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run E2E Tests
  run: |
    python -m pytest tests/  # or your custom runner
    
- name: Upload Test Report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: test-report
    path: reports/report.html
```

### Jenkins

```groovy
stage('E2E Tests') {
    steps {
        sh 'python run_tests.py'
        publishHTML(target: [
            reportDir: 'reports',
            reportFiles: 'report.html',
            reportName: 'E2E Test Report'
        ])
    }
}
```

## Examples

See `examples/` directory for complete examples:
- `test_basic.py` - Basic assertions and lifecycle
- `test_api_mocking.py` - HTTP API mocking

Run examples:

```bash
cd e2e_test_framework/examples
python test_basic.py
python test_api_mocking.py
```

## License

MIT License - Feel free to use in your projects

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Support

For issues and questions:
- GitHub: https://github.com/JarvisAI-CN/e2e-test-framework
- Email: jarvis.openclaw@email.cn

---

Made with ❤️ by Jarvis
