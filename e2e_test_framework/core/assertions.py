"""
Core assertion library with chainable API.
"""

from typing import Any, Callable, Optional
from datetime import datetime
import re


class AssertionFailure(AssertionError):
    """Custom assertion error with details."""
    def __init__(self, message: str, expected: Any = None, actual: Any = None):
        details = f"\n  Expected: {expected}\n  Actual: {actual}" if expected is not None else ""
        super().__init__(f"❌ {message}{details}")
        self.expected = expected
        self.actual = actual
        self.timestamp = datetime.now()


class AssertionChain:
    """Chainable assertion API."""
    
    def __init__(self, value: Any, negated: bool = False):
        self._value = value
        self._negated = negated
        self._actual = value
    
    def not_(self) -> 'AssertionChain':
        """Negate the assertion."""
        return AssertionChain(self._value, not self._negated)
    
    not_ = not_  # Alias
    
    def _fail(self, message: str, expected: Any = None):
        """Raise assertion error."""
        if self._negated:
            return  # Negated assertions pass on failure
        raise AssertionFailure(message, expected, self._actual)
    
    def _pass(self, condition: bool, message: str, expected: Any = None):
        """Check condition and fail/pass accordingly."""
        should_pass = condition if not self._negated else not condition
        if not should_pass:
            self._fail(message, expected)
    
    # Equality assertions
    def to_eq(self, expected: Any) -> 'AssertionChain':
        """Equal to."""
        self._pass(self._value == expected, "values are not equal", expected)
        return self
    
    def to_be(self, expected: Any) -> 'AssertionChain':
        """Alias for to_eq."""
        return self.to_eq(expected)
    
    def to_deep_eq(self, expected: Any) -> 'AssertionChain':
        """Deep equality for dicts/lists."""
        def deep_compare(a, b, path=""):
            if type(a) != type(b):
                return False, f"{path} type mismatch: {type(a)} vs {type(b)}"
            if isinstance(a, dict):
                if set(a.keys()) != set(b.keys()):
                    return False, f"{path} keys mismatch"
                for k in a:
                    result = deep_compare(a[k], b[k], f"{path}.{k}")
                    if not result[0]:
                        return result
            elif isinstance(a, list):
                if len(a) != len(b):
                    return False, f"{path} length mismatch"
                for i, (x, y) in enumerate(zip(a, b)):
                    result = deep_compare(x, y, f"{path}[{i}]")
                    if not result[0]:
                        return result
            else:
                return a == b, ""
            return True, ""
        
        equal, msg = deep_compare(self._value, expected)
        self._pass(equal, f"deep equality failed: {msg}", expected)
        return self
    
    # Type assertions
    def to_be_type(self, expected_type: type) -> 'AssertionChain':
        """Type check."""
        self._pass(isinstance(self._value, expected_type),
                   f"value is not {expected_type.__name__}", expected_type.__name__)
        return self
    
    def to_be_none(self) -> 'AssertionChain':
        """None check."""
        self._pass(self._value is None, "value is not None", None)
        return self
    
    def to_be_truthy(self) -> 'AssertionChain':
        """Truthy check."""
        self._pass(bool(self._value), "value is falsy", "truthy")
        return self
    
    def to_be_falsy(self) -> 'AssertionChain':
        """Falsy check."""
        self._pass(not bool(self._value), "value is truthy", "falsy")
        return self
    
    # Numeric assertions
    def to_be_gt(self, expected: Any) -> 'AssertionChain':
        """Greater than."""
        self._pass(self._value > expected, f"{self._value} is not > {expected}", f">{expected}")
        return self
    
    def to_be_gte(self, expected: Any) -> 'AssertionChain':
        """Greater or equal."""
        self._pass(self._value >= expected, f"{self._value} is not >= {expected}", f">={expected}")
        return self
    
    def to_be_lt(self, expected: Any) -> 'AssertionChain':
        """Less than."""
        self._pass(self._value < expected, f"{self._value} is not < {expected}", f"<{expected}")
        return self
    
    def to_be_lte(self, expected: Any) -> 'AssertionChain':
        """Less or equal."""
        self._pass(self._value <= expected, f"{self._value} is not <= {expected}", f"<={expected}")
        return self
    
    def to_be_close_to(self, expected: float, tolerance: float = 0.001) -> 'AssertionChain':
        """Approximate equality."""
        delta = abs(self._value - expected)
        self._pass(delta <= tolerance,
                   f"{self._value} is not close to {expected} (tolerance: {tolerance})",
                   f"{expected} ± {tolerance}")
        return self
    
    # String assertions
    def to_contain(self, expected: str) -> 'AssertionChain':
        """Substring check."""
        self._pass(expected in str(self._value),
                   f"'{self._value}' does not contain '{expected}'",
                   f"contains '{expected}'")
        return self
    
    def to_match(self, pattern: str, flags: int = 0) -> 'AssertionChain':
        """Regex match."""
        match = re.search(pattern, str(self._value), flags)
        self._pass(match is not None,
                   f"'{self._value}' does not match pattern '{pattern}'",
                   f"matches /{pattern}/")
        return self
    
    def to_start_with(self, expected: str) -> 'AssertionChain':
        """Prefix check."""
        self._pass(str(self._value).startswith(expected),
                   f"'{self._value}' does not start with '{expected}'",
                   f"starts with '{expected}'")
        return self
    
    def to_end_with(self, expected: str) -> 'AssertionChain':
        """Suffix check."""
        self._pass(str(self._value).endswith(expected),
                   f"'{self._value}' does not end with '{expected}'",
                   f"ends with '{expected}'")
        return self
    
    # Collection assertions
    def to_have_length(self, expected: int) -> 'AssertionChain':
        """Length check."""
        actual = len(self._value)
        self._pass(actual == expected,
                   f"length is {actual}, expected {expected}",
                   f"length {expected}")
        return self
    
    def to_include(self, item: Any) -> 'AssertionChain':
        """Array/contains check."""
        self._pass(item in self._value,
                   f"{item} not found in collection",
                   f"includes {item}")
        return self
    
    def to_have_key(self, key: str) -> 'AssertionChain':
        """Dict key check."""
        self._pass(key in self._value,
                   f"key '{key}' not found in dict",
                   f"has key '{key}'")
        return self
    
    def to_have_property(self, prop: str) -> 'AssertionChain':
        """Object property check."""
        self._pass(hasattr(self._value, prop),
                   f"property '{prop}' not found",
                   f"has property '{prop}'")
        return self
    
    # Callable assertions
    def to_throw(self, error_type: type = Exception) -> 'AssertionChain':
        """Exception check."""
        if not callable(self._value):
            raise AssertionFailure("value is not callable")
        
        try:
            self._value()
            if self._negated:
                return self  # Expected no throw, got no throw - pass in negated mode
            self._fail("function did not throw", error_type.__name__)
        except error_type:
            return self  # Threw expected error
        except Exception as e:
            self._fail(f"function threw {type(e).__name__} instead of {error_type.__name__}",
                      error_type.__name__)
        return self
    
    # Async callable assertions
    async def to_throw_async(self, error_type: type = Exception) -> 'AssertionChain':
        """Async exception check."""
        if not callable(self._value):
            raise AssertionFailure("value is not callable")
        
        try:
            if hasattr(self._value, '__await__'):
                await self._value
            else:
                await self._value()
            self._fail("async function did not throw", error_type.__name__)
        except error_type:
            return self
        except Exception as e:
            self._fail(f"async function threw {type(e).__name__} instead of {error_type.__name__}",
                      error_type.__name__)
        return self


# Factory function
def expect(value: Any) -> AssertionChain:
    """
    Create an assertion chain.
    
    Examples:
        expect(5).to_be_gt(3)
        expect("hello").to_contain("ell")
        expect({"a": 1}).to_have_key("a")
        expect([1, 2, 3]).to_have_length(3)
        expect(lambda: 1/0).to_throw(ZeroDivisionError)
    """
    return AssertionChain(value)


# BDD-style aliases
def given(value: Any) -> AssertionChain:
    """BDD-style: Given a value..."""
    return expect(value)


def when(value: Any) -> AssertionChain:
    """BDD-style: When a value..."""
    return expect(value)


def then(value: Any) -> AssertionChain:
    """BDD-style: Then expect..."""
    return expect(value)


# Direct assertion functions
def assert_equal(actual: Any, expected: Any, message: str = ""):
    """Simple equality assertion."""
    if actual != expected:
        msg = message or f"Expected {expected}, got {actual}"
        raise AssertionFailure(msg, expected, actual)


def assert_true(value: Any, message: str = ""):
    """Assert truthy."""
    if not value:
        raise AssertionFailure(message or f"Expected truthy, got {value}")


def assert_false(value: Any, message: str = ""):
    """Assert falsy."""
    if value:
        raise AssertionFailure(message or f"Expected falsy, got {value}")


def assert_in(item: Any, collection: Any, message: str = ""):
    """Assert item in collection."""
    if item not in collection:
        raise AssertionFailure(message or f"{item} not in {collection}")


def assert_raises(func: Callable, error_type: type = Exception):
    """Assert function raises exception."""
    try:
        func()
        raise AssertionFailure(f"Expected {error_type.__name__} to be raised")
    except error_type:
        pass
    except Exception as e:
        raise AssertionFailure(f"Expected {error_type.__name__}, got {type(e).__name__}")
