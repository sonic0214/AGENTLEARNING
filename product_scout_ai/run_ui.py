#!/usr/bin/env python
"""
ProductScout AI - Gradio UI Launcher

Usage:
    python run_ui.py [options]

Options:
    --host HOST     Server hostname (default: 0.0.0.0)
    --port PORT     Server port (default: 7860)
    --share         Create a public link
    --debug         Enable debug mode
"""
import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure compatibility module is loaded before other imports
try:
    from src.utils.compatibility import *
except ImportError as e:
    print(f"Warning: Could not import compatibility module: {e}")
    print("Some features may not work correctly with Python 3.9")

from src.ui.app import main


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ProductScout AI - Gradio UI Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_ui.py
    python run_ui.py --port 8080
    python run_ui.py --share --debug
        """
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server hostname (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Server port (default: 7860)"
    )

    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public Gradio link"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🔍 ProductScout AI - 产品机会分析平台                    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    print(f"Starting server at http://{args.host}:{args.port}")
    if args.share:
        print("Public link will be generated...")
    print()

    main(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        debug=args.debug
    )
