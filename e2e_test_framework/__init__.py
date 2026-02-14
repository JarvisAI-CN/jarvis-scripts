"""
E2E Test Framework - A lightweight, extensible end-to-end testing framework.

Main exports:
- expect: Assertion chain API
- TestCase: Base test case class
- TestRunner: Test execution engine
- TestSuite: Test suite organizer
- test, skip, retry, timeout: Decorators
"""

# Core
from .core.assertions import (
    expect,
    AssertionChain,
    AssertionFailure,
    # Direct assertions
    assert_equal,
    assert_true,
    assert_false,
    assert_in,
    assert_raises,
    # BDD aliases
    given,
    when,
    then
)

from .core.case import (
    TestCase,
    TestResult,
    TestCaseInfo,
    # Lifecycle decorators
    setup,
    teardown,
    setup_class,
    teardown_class,
    # Test decorators
    test,
    test_case,
    skip,
    skip_if,
    retry,
    timeout,
    tags,
    depends_on,
    priority,
    apply_hooks
)

from .core.runner import (
    TestRunner,
    TestSuite,
    TestRunSummary,
    create_suite,
    run_tests,
    discover_tests
)

# Mocks
from .mocks.http_mock import (
    HttpMock,
    ApiMock,
    ResourceMock,
    MockRequest,
    MockResponse,
    # Utilities
    mock_api_response,
    mock_api_error,
    mock_sequence,
    mock_conditional
)

# Reporters
from .reporters.html_reporter import (
    HTMLReporter,
    generate_html_report
)

from .reporters.json_reporter import (
    JSONReporter,
    JUnitReporter,
    generate_json_report,
    generate_junit_report,
    generate_github_annotations,
    generate_teamcity_messages
)

from .reporters.console_reporter import (
    ConsoleReporter,
    ProgressReporter,
    print_test_summary,
    create_console_reporter
)

__version__ = "1.0.0"
__author__ = "Jarvis <jarvis.openclaw@email.cn>"
__description__ = "Lightweight, extensible E2E testing framework with async support"

__all__ = [
    # Core assertions
    "expect",
    "AssertionChain",
    "AssertionFailure",
    "assert_equal",
    "assert_true",
    "assert_false",
    "assert_in",
    "assert_raises",
    "given",
    "when",
    "then",
    
    # Test case
    "TestCase",
    "TestResult",
    "TestCaseInfo",
    "setup",
    "teardown",
    "setup_class",
    "teardown_class",
    "test",
    "test_case",
    "skip",
    "skip_if",
    "retry",
    "timeout",
    "tags",
    "depends_on",
    "priority",
    "apply_hooks",
    
    # Runner
    "TestRunner",
    "TestSuite",
    "TestRunSummary",
    "create_suite",
    "run_tests",
    "discover_tests",
    
    # Mocks
    "HttpMock",
    "ApiMock",
    "ResourceMock",
    "MockRequest",
    "MockResponse",
    "mock_api_response",
    "mock_api_error",
    "mock_sequence",
    "mock_conditional",
    
    # Reporters
    "HTMLReporter",
    "generate_html_report",
    "JSONReporter",
    "JUnitReporter",
    "generate_json_report",
    "generate_junit_report",
    "generate_github_annotations",
    "generate_teamcity_messages",
    "ConsoleReporter",
    "ProgressReporter",
    "print_test_summary",
    "create_console_reporter",
]


# Convenience aliases
def create_test(*args, **kwargs):
    """Alias for test_case decorator."""
    return test_case(*args, **kwargs)


def describe(name: str):
    """BDD-style test group."""
    def decorator(cls):
        cls._test_info = TestCaseInfo(name=name)
        return cls
    return decorator


def it(description: str):
    """BDD-style test definition."""
    def decorator(func):
        return test(name=description)(func)
    return decorator


# Add to __all__
__all__.extend(["create_test", "describe", "it"])
