"""
UI package for ProductScout AI.

This package provides the Gradio-based web interface.
"""
from .app import create_app, main

__all__ = [
    "create_app",
    "main",
]
