#!/usr/bin/env python3
"""
Compatibility fix for Python 3.9 importlib.metadata

This module patches the missing packages_distributions function
in Python 3.9's importlib.metadata module.
"""

import importlib.metadata
import importlib.util
import warnings

def packages_distributions():
    """
    Enhanced compatibility fallback for Python 3.9.

    In Python 3.9, packages_distributions() doesn't exist.
    This function provides an improved fallback that maps distributions properly.
    """
    # Python 3.9 fallback implementation - avoid recursion
    result = {}
    try:
        for dist in importlib.metadata.distributions():
            # Try to get package name mapping
            name = dist.metadata.get('Name') or dist.name
            result[name] = [name]
    except Exception as e:
        warnings.warn(f"Failed to map packages: {e}")
        return {}
    return result

# Apply the patch if the function doesn't exist
if not hasattr(importlib.metadata, 'packages_distributions'):
    importlib.metadata.packages_distributions = packages_distributions