"""
Safe access utilities for navigating nested data structures.

Provides functions to safely access list elements and navigate nested
dictionaries/lists without raising IndexError or KeyError.
"""
from typing import Any, Optional, TypeVar, List

T = TypeVar('T')


def safe_list_get(lst: Any, index: int, default: Optional[T] = None) -> Optional[T]:
    """
    Safely get item from list with bounds checking.

    Args:
        lst: The object to access (must be a list)
        index: Index to access
        default: Default value if access fails

    Returns:
        Item at index or default value

    Example:
        >>> safe_list_get([1, 2, 3], 0)
        1
        >>> safe_list_get([1, 2, 3], 10, default=99)
        99
        >>> safe_list_get({"not": "list"}, 0)
        None
    """
    if not isinstance(lst, list):
        return default
    if index < 0 or index >= len(lst):
        return default
    return lst[index]


def safe_dict_get(obj: Any, key: str, default: Optional[T] = None) -> Optional[T]:
    """
    Safely get value from dictionary.

    Args:
        obj: The object to access (must be a dict)
        key: Key to access
        default: Default value if access fails

    Returns:
        Value at key or default value

    Example:
        >>> safe_dict_get({"name": "test"}, "name")
        'test'
        >>> safe_dict_get({"name": "test"}, "missing", "N/A")
        'N/A'
        >>> safe_dict_get([1, 2, 3], "name")
        None
    """
    if not isinstance(obj, dict):
        return default
    return obj.get(key, default)


def safe_dict_path(obj: Any, path: str, default: Optional[T] = None) -> Optional[T]:
    """
    Safely navigate nested dict/list structures using a path string.

    Args:
        obj: Object to navigate
        path: Dot-separated path (e.g., "content.parts.0.text")
              Numbers are treated as list indices
        default: Default value if path doesn't exist

    Returns:
        Value at path or default value

    Example:
        >>> data = {"content": {"parts": [{"text": "hello"}]}}
        >>> safe_dict_path(data, "content.parts.0.text")
        'hello'
        >>> safe_dict_path(data, "content.parts.1.text", "N/A")
        'N/A'
        >>> safe_dict_path(data, "invalid.path")
        None
    """
    current = obj
    for key in path.split('.'):
        if key.isdigit():
            # List index
            current = safe_list_get(current, int(key))
            if current is None:
                return default
        elif isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current


def is_non_empty_list(obj: Any) -> bool:
    """
    Check if object is a non-empty list.

    Args:
        obj: Object to check

    Returns:
        True if obj is a list with at least one element

    Example:
        >>> is_non_empty_list([1, 2, 3])
        True
        >>> is_non_empty_list([])
        False
        >>> is_non_empty_list("not a list")
        False
        >>> is_non_empty_list(None)
        False
    """
    return isinstance(obj, list) and len(obj) > 0


def is_non_empty_dict(obj: Any) -> bool:
    """
    Check if object is a non-empty dictionary.

    Args:
        obj: Object to check

    Returns:
        True if obj is a dict with at least one key

    Example:
        >>> is_non_empty_dict({"key": "value"})
        True
        >>> is_non_empty_dict({})
        False
        >>> is_non_empty_dict([1, 2, 3])
        False
    """
    return isinstance(obj, dict) and len(obj) > 0


def get_nested_value(obj: Any, keys: List[Any], default: Optional[T] = None) -> Optional[T]:
    """
    Get value from nested structure using a list of keys/indices.

    Args:
        obj: Object to navigate
        keys: List of keys (strings for dicts, ints for lists)
        default: Default value if path doesn't exist

    Returns:
        Value at path or default value

    Example:
        >>> data = {"user": {"profile": {"age": 25}}}
        >>> get_nested_value(data, ["user", "profile", "age"])
        25
        >>> data = {"items": [{"name": "a"}, {"name": "b"}]}
        >>> get_nested_value(data, ["items", 1, "name"])
        'b'
    """
    current = obj
    for key in keys:
        if isinstance(key, int):
            current = safe_list_get(current, key)
        elif isinstance(key, str):
            current = safe_dict_get(current, key)
        else:
            return default

        if current is None:
            return default

    return current
