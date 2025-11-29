"""
CLI package for ProductScout AI.

This package provides the command-line interface.
"""
from .main import main, create_parser, parse_args

__all__ = [
    "main",
    "create_parser",
    "parse_args",
]
