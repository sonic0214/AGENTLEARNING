"""
CLI interface for ProductScout AI.

This module provides the command-line interface for running
product opportunity analyses.
"""
import argparse
import asyncio
import sys
from typing import Optional

from src.config.settings import Settings
from src.schemas.input_schemas import AnalysisRequest
from src.services import analysis_service as analysis_svc
from src.services import export_service as export_svc


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser for the CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="product_scout",
        description="ProductScout AI - Product Opportunity Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  product_scout analyze "portable blender"
  product_scout analyze "smart watch" --market EU --budget high
  product_scout analyze "gaming mouse" --output json --file report.json
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a product category opportunity"
    )
    analyze_parser.add_argument(
        "category",
        type=str,
        help="Product category to analyze"
    )
    analyze_parser.add_argument(
        "--market",
        type=str,
        default="US",
        choices=["US", "EU", "UK", "CA", "AU", "JP", "DE", "FR"],
        help="Target market (default: US)"
    )
    analyze_parser.add_argument(
        "--budget", "-b",
        type=str,
        default="medium",
        choices=["low", "medium", "high"],
        help="Budget range (default: medium)"
    )
    analyze_parser.add_argument(
        "--model", "-M",
        type=str,
        default="amazon_fba",
        choices=["amazon_fba", "dropshipping", "private_label", "wholesale"],
        help="Business model (default: amazon_fba)"
    )
    analyze_parser.add_argument(
        "--output", "-o",
        type=str,
        default="markdown",
        choices=["json", "markdown", "summary"],
        help="Output format (default: markdown)"
    )
    analyze_parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="Output file path (default: stdout)"
    )
    analyze_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    # Version command
    parser.add_argument(
        "--version", "-V",
        action="version",
        version="ProductScout AI v0.1.0"
    )

    return parser


def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        args: Optional argument list (uses sys.argv if None)

    Returns:
        Parsed arguments namespace
    """
    parser = create_parser()
    return parser.parse_args(args)


async def run_analysis(args: argparse.Namespace) -> int:
    """
    Run the analysis command.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Create request
    request = AnalysisRequest(
        category=args.category,
        target_market=args.market,
        budget_range=args.budget,
        business_model=args.model
    )

    # Create service
    service = analysis_svc.create_analysis_service()

    if args.verbose:
        print(f"Analyzing: {args.category}")
        print(f"Market: {args.market}")
        print(f"Budget: {args.budget}")
        print(f"Model: {args.model}")
        print("-" * 40)

    # Define progress callback
    def on_progress(phase: str, message: str) -> None:
        if args.verbose:
            print(f"[{phase}] {message}")

    try:
        # Run analysis
        result = await service.analyze(request, on_progress=on_progress)

        if not result.success:
            print(f"Error: {result.error}", file=sys.stderr)
            return 1

        # Format output
        if args.output == "json":
            output = export_svc.export_to_json(result)
        elif args.output == "markdown":
            output = export_svc.export_to_markdown(result)
        else:  # summary
            exporter = export_svc.create_export_service()
            output = exporter.to_summary(result)

        # Write output
        if args.file:
            with open(args.file, 'w') as f:
                f.write(output)
            if args.verbose:
                print(f"Output written to: {args.file}")
        else:
            print(output)

        return 0

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Optional argument list (uses sys.argv if None)

    Returns:
        Exit code
    """
    parsed_args = parse_args(args)

    if parsed_args.command is None:
        create_parser().print_help()
        return 0

    if parsed_args.command == "analyze":
        return asyncio.run(run_analysis(parsed_args))

    return 0


if __name__ == "__main__":
    sys.exit(main())
