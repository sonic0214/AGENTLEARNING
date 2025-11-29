"""
Result type for structured error handling.

Provides a Result<T, E> pattern similar to Rust for handling operations
that can fail without using exceptions.
"""
from typing import Generic, TypeVar, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

T = TypeVar('T')  # Success type
E = TypeVar('E')  # Error type
U = TypeVar('U')  # Mapped success type
F = TypeVar('F')  # Mapped error type


class ErrorCategory(Enum):
    """Business-level error categories for better error handling."""
    AGENT_EXECUTION = "agent_execution"
    PARSING = "parsing"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    EXTERNAL_API = "external_api"
    TIMEOUT = "timeout"
    RESOURCE = "resource"


@dataclass
class ErrorContext:
    """
    Contextual information about an error.

    Attributes:
        category: Business-level category of the error
        message: User-friendly error message
        technical_detail: Technical details for logging (not shown to users)
        phase: Which phase of the pipeline failed
        agent_name: Name of the agent that failed (if applicable)
        timestamp: When the error occurred
    """
    category: ErrorCategory
    message: str
    technical_detail: Optional[str] = None
    phase: Optional[str] = None
    agent_name: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category.value,
            "message": self.message,
            "technical_detail": self.technical_detail,
            "phase": self.phase,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp
        }

    def user_message(self) -> str:
        """Get user-friendly error message without technical details."""
        return self.message


class Result(Generic[T, E]):
    """
    Result type for error handling (similar to Rust's Result<T,E>).

    A Result represents either success (Ok) or failure (Err).
    This allows explicit error handling without exceptions.

    Example:
        >>> result = safe_operation()
        >>> if result.is_ok():
        ...     value = result.unwrap()
        ...     print(f"Success: {value}")
        ... else:
        ...     error = result.unwrap_err()
        ...     print(f"Error: {error}")
    """

    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        if (value is None and error is None) or (value is not None and error is not None):
            raise ValueError("Result must have exactly one of value or error")
        self._value = value
        self._error = error

    @classmethod
    def Ok(cls, value: T) -> 'Result[T, E]':
        """Create a successful Result containing a value."""
        return cls(value=value)

    @classmethod
    def Err(cls, error: E) -> 'Result[T, E]':
        """Create a failed Result containing an error."""
        return cls(error=error)

    def is_ok(self) -> bool:
        """Check if this Result is Ok."""
        return self._value is not None

    def is_err(self) -> bool:
        """Check if this Result is Err."""
        return self._error is not None

    def unwrap(self) -> T:
        """
        Get the Ok value.

        Raises:
            ValueError: If called on an Err result
        """
        if self._value is None:
            raise ValueError(f"Called unwrap on Err value: {self._error}")
        return self._value

    def unwrap_err(self) -> E:
        """
        Get the Err value.

        Raises:
            ValueError: If called on an Ok result
        """
        if self._error is None:
            raise ValueError("Called unwrap_err on Ok value")
        return self._error

    def unwrap_or(self, default: T) -> T:
        """Get the Ok value or return a default if Err."""
        return self._value if self._value is not None else default

    def unwrap_or_else(self, f: Callable[[E], T]) -> T:
        """Get the Ok value or compute it from the error."""
        if self._value is not None:
            return self._value
        return f(self._error)

    def map(self, f: Callable[[T], U]) -> 'Result[U, E]':
        """
        Map the Ok value using a function, leave Err unchanged.

        Example:
            >>> Result.Ok(5).map(lambda x: x * 2)  # Result.Ok(10)
            >>> Result.Err("error").map(lambda x: x * 2)  # Result.Err("error")
        """
        if self.is_ok():
            return Result.Ok(f(self._value))
        return Result.Err(self._error)

    def map_err(self, f: Callable[[E], F]) -> 'Result[T, F]':
        """
        Map the Err value using a function, leave Ok unchanged.

        Example:
            >>> Result.Ok(5).map_err(str)  # Result.Ok(5)
            >>> Result.Err(404).map_err(str)  # Result.Err("404")
        """
        if self.is_err():
            return Result.Err(f(self._error))
        return Result.Ok(self._value)

    def and_then(self, f: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """
        Chain another operation that returns a Result.
        Also known as flatMap or bind in other languages.

        Example:
            >>> def parse_int(s: str) -> Result[int, str]:
            ...     try:
            ...         return Result.Ok(int(s))
            ...     except ValueError:
            ...         return Result.Err("not a number")
            >>> Result.Ok("42").and_then(parse_int)  # Result.Ok(42)
            >>> Result.Ok("abc").and_then(parse_int)  # Result.Err("not a number")
        """
        if self.is_ok():
            return f(self._value)
        return Result.Err(self._error)

    def __repr__(self) -> str:
        if self.is_ok():
            return f"Result.Ok({self._value!r})"
        return f"Result.Err({self._error!r})"
