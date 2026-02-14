"""
Test case base class and decorators.
"""

from typing import Callable, List, Optional, Any, Dict
from functools import wraps
from dataclasses import dataclass, field
from datetime import datetime
import inspect
import asyncio


@dataclass
class TestCaseInfo:
    """Test case metadata."""
    name: str
    description: str = ""
    timeout: float = 30.0  # seconds
    retries: int = 0
    skip: bool = False
    skip_reason: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    retry_delay: float = 1.0
    priority: int = 0  # Higher runs first
    owner: str = ""
    severity: str = "normal"  # trivial, normal, critical, blocker


class TestResult:
    """Test execution result."""
    
    def __init__(self, name: str):
        self.name = name
        self.status = "pending"  # pending, running, passed, failed, skipped, timeout
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.duration: float = 0.0
        self.error: Optional[Exception] = None
        self.error_trace: Optional[str] = None
        self.retry_count: int = 0
        self.attempts: List[Dict[str, Any]] = field(default_factory=list)
        self.metadata: Dict[str, Any] = field(default_factory=dict)
        self.screenshots: List[str] = field(default_factory=list)
        self.logs: List[str] = field(default_factory=list)
        self.assertions_passed: int = 0
        self.assertions_failed: int = 0
    
    def start(self):
        """Start test execution."""
        self.status = "running"
        self.start_time = datetime.now()
    
    def end(self, status: str, error: Optional[Exception] = None):
        """End test execution."""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = status
        self.error = error
        if error:
            import traceback
            self.error_trace = traceback.format_exc()
    
    def add_attempt(self, status: str, error: Optional[Exception] = None):
        """Record a retry attempt."""
        self.attempts.append({
            "attempt": len(self.attempts) + 1,
            "status": status,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "name": self.name,
            "status": self.status,
            "duration": self.duration,
            "error": str(self.error) if self.error else None,
            "retry_count": self.retry_count,
            "attempts": self.attempts,
            "assertions": {
                "passed": self.assertions_passed,
                "failed": self.assertions_failed
            },
            "metadata": self.metadata
        }


class TestCase:
    """Base test case class."""
    
    # Class-level metadata
    _test_info: TestCaseInfo = None
    _setup_func: Optional[Callable] = None
    _teardown_func: Optional[Callable] = None
    _setup_class_func: Optional[Callable] = None
    _teardown_class_func: Optional[Callable] = None
    
    def __init__(self):
        self.result = TestResult(self.__class__.__name__)
        self.shared_context: Dict[str, Any] = {}
    
    @classmethod
    def get_info(cls) -> TestCaseInfo:
        """Get test case info."""
        if cls._test_info is None:
            cls._test_info = TestCaseInfo(name=cls.__name__)
        return cls._test_info
    
    async def setup(self):
        """Setup before each test."""
        pass
    
    async def teardown(self):
        """Teardown after each test."""
        pass
    
    @classmethod
    async def setup_class(cls):
        """Setup once before all tests in class."""
        pass
    
    @classmethod
    async def teardown_class(cls):
        """Teardown once after all tests in class."""
        pass
    
    async def run(self) -> TestResult:
        """Execute the test case."""
        info = self.get_info()
        
        if info.skip:
            self.result.end("skipped")
            return self.result
        
        # Run setup_class if not already run
        if self._setup_class_func and not hasattr(self.__class__, '_setup_class_run'):
            await self._setup_class_func()
            self.__class__._setup_class_run = True
        
        try:
            self.result.start()
            
            # Setup with timeout
            try:
                await asyncio.wait_for(self.setup(), timeout=5.0)
            except asyncio.TimeoutError:
                self.result.end("failed", Exception("Setup timeout"))
                return self.result
            
            # Run test with retries
            last_error = None
            for attempt in range(info.retries + 1):
                self.result.retry_count = attempt
                try:
                    await asyncio.wait_for(
                        self.execute_test(),
                        timeout=info.timeout
                    )
                    self.result.add_attempt("passed")
                    break
                except asyncio.TimeoutError:
                    last_error = Exception(f"Test timeout after {info.timeout}s")
                    self.result.add_attempt("timeout", last_error)
                    if attempt < info.retries:
                        await asyncio.sleep(info.retry_delay)
                except Exception as e:
                    last_error = e
                    self.result.add_attempt("failed", e)
                    if attempt < info.retries:
                        await asyncio.sleep(info.retry_delay)
            
            if last_error:
                raise last_error
            
            # Teardown
            try:
                await asyncio.wait_for(self.teardown(), timeout=5.0)
            except asyncio.TimeoutError:
                pass  # Don't fail test if teardown times out
            
            self.result.end("passed")
            
        except Exception as e:
            self.result.end("failed", e)
        
        finally:
            # Run teardown_class on last test
            if self._teardown_class_func and not hasattr(self.__class__, '_teardown_class_run'):
                await self._teardown_class_func()
                self.__class__._teardown_class_run = True
        
        return self.result
    
    async def execute_test(self):
        """Override this method to implement test logic."""
        raise NotImplementedError("Subclasses must implement execute_test()")


# Decorators

def test(
    name: str = None,
    description: str = "",
    timeout: float = 30.0,
    retries: int = 0,
    tags: List[str] = None,
    priority: int = 0,
    owner: str = "",
    severity: str = "normal"
):
    """
    Decorator to mark a method as a test.
    
    Example:
        @test(name="User login", timeout=10, tags=["auth", "smoke"])
        async def test_user_login(self):
            expect(self.user.email).to_contain("@")
    """
    def decorator(func):
        # Create a test class from the function
        class FunctionTest(TestCase):
            async def execute_test(self):
                if asyncio.iscoroutinefunction(func):
                    return await func(self)
                else:
                    return func(self)
        
        FunctionTest.__name__ = name or func.__name__
        FunctionTest._test_info = TestCaseInfo(
            name=name or func.__name__,
            description=description,
            timeout=timeout,
            retries=retries,
            tags=tags or [],
            priority=priority,
            owner=owner,
            severity=severity
        )
        
        return FunctionTest
    return decorator


def skip(reason: str = ""):
    """Skip test execution."""
    def decorator(cls):
        if isinstance(cls, type):
            info = cls.get_info()
            info.skip = True
            info.skip_reason = reason
        return cls
    return decorator


def skip_if(condition: bool, reason: str = ""):
    """Skip test if condition is true."""
    def decorator(cls):
        if condition:
            info = cls.get_info()
            info.skip = True
            info.skip_reason = reason or f"Condition {condition} is true"
        return cls
    return decorator


def retry(count: int, delay: float = 1.0):
    """Retry failed test."""
    def decorator(cls):
        if isinstance(cls, type):
            info = cls.get_info()
            info.retries = count
            info.retry_delay = delay
        return cls
    return decorator


def timeout(seconds: float):
    """Set test timeout."""
    def decorator(cls):
        if isinstance(cls, type):
            info = cls.get_info()
            info.timeout = seconds
        return cls
    return decorator


def tags(*tag_list: str):
    """Add tags to test."""
    def decorator(cls):
        if isinstance(cls, type):
            info = cls.get_info()
            info.tags.extend(tag_list)
        return cls
    return decorator


def depends_on(*test_names: str):
    """Add test dependencies."""
    def decorator(cls):
        if isinstance(cls, type):
            info = cls.get_info()
            info.dependencies.extend(test_names)
        return cls
    return decorator


def priority(level: int):
    """Set test priority (higher runs first)."""
    def decorator(cls):
        if isinstance(cls, type):
            info = cls.get_info()
            info.priority = level
        return cls
    return decorator


# Lifecycle decorators

def setup(func):
    """Register setup function."""
    setattr(func, '_e2e_hook', 'setup')
    return func


def teardown(func):
    """Register teardown function."""
    setattr(func, '_e2e_hook', 'teardown')
    return func


def setup_class(func):
    """Register setup_class function."""
    setattr(func, '_e2e_hook', 'setup_class')
    return func


def teardown_class(func):
    """Register teardown_class function."""
    setattr(func, '_e2e_hook', 'teardown_class')
    return func


def apply_hooks(test_class):
    """Apply lifecycle hooks to test class."""
    for name, method in inspect.getmembers(test_class, predicate=inspect.isfunction):
        hook = getattr(method, '_e2e_hook', None)
        if hook == 'setup':
            test_class._setup_func = method
        elif hook == 'teardown':
            test_class._teardown_func = method
        elif hook == 'setup_class':
            test_class._setup_class_func = staticmethod(method)
        elif hook == 'teardown_class':
            test_class._teardown_class_func = staticmethod(method)
    return test_class


def test_case(
    name: str = None,
    description: str = "",
    timeout: float = 30.0,
    retries: int = 0,
    tags: List[str] = None
):
    """
    Class decorator for test cases.
    
    Example:
        @test_case(name="Auth tests", timeout=60, tags=["auth"])
        class TestAuthentication(TestCase):
            async def execute_test(self):
                expect(True).to_be_true()
    """
    def decorator(cls):
        cls._test_info = TestCaseInfo(
            name=name or cls.__name__,
            description=description,
            timeout=timeout,
            retries=retries,
            tags=tags or []
        )
        return apply_hooks(cls)
    return decorator
