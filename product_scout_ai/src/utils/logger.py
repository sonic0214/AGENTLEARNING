"""
Logging utilities for ProductScout AI.

This module provides centralized logging configuration and utilities.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for formatted console output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def setup_logger(
    name: str = "product_scout",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger:
    """
    Setup and configure logger with console and file handlers.

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional path to log file
        console: Whether to add console handler

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_analysis_start(logger: logging.Logger, category: str, market: str):
    """Log analysis start."""
    logger.info(f"{Colors.OKBLUE}{'='*60}{Colors.ENDC}")
    logger.info(f"{Colors.OKBLUE}🚀 Starting analysis: {category} (Market: {market}){Colors.ENDC}")
    logger.info(f"{Colors.OKBLUE}{'='*60}{Colors.ENDC}")


def log_phase_start(logger: logging.Logger, phase: str, description: str):
    """Log phase start."""
    logger.info(f"{Colors.OKCYAN}▶️  Phase: {phase} - {description}{Colors.ENDC}")


def log_phase_complete(logger: logging.Logger, phase: str, duration: float):
    """Log phase completion."""
    logger.info(f"{Colors.OKGREEN}✅ Phase {phase} completed in {duration:.2f}s{Colors.ENDC}")


def log_phase_error(logger: logging.Logger, phase: str, error: str):
    """Log phase error."""
    logger.error(f"{Colors.FAIL}❌ Phase {phase} failed: {error}{Colors.ENDC}")


def log_agent_call(logger: logging.Logger, agent_name: str, action: str):
    """Log agent API call."""
    logger.info(f"{Colors.OKCYAN}  🤖 Agent: {agent_name} - {action}{Colors.ENDC}")


def log_agent_input_detailed(logger: logging.Logger, agent_name: str, instruction: str, tools: list = None):
    """Log detailed agent input with醒目 formatting."""
    logger.info(f"{Colors.BOLD}{Colors.HEADER}{'🔥 AGENT INPUT - ' + agent_name.upper() + ' 🔥'}{Colors.ENDC}")
    logger.info(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")

    # Log instruction
    logger.info(f"{Colors.OKBLUE}📝 INSTRUCTION:{Colors.ENDC}")
    if len(instruction) > 500:
        logger.info(f"{Colors.OKCYAN}{instruction[:500]}...[truncated]{Colors.ENDC}")
    else:
        logger.info(f"{Colors.OKCYAN}{instruction}{Colors.ENDC}")

    # Log tools if available
    if tools:
        logger.info(f"{Colors.OKBLUE}🔧 TOOLS AVAILABLE:{Colors.ENDC}")
        for tool in tools:
            tool_name = getattr(tool, 'name', str(tool))
            logger.info(f"{Colors.OKCYAN}  - {tool_name}{Colors.ENDC}")

    logger.info(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")


def log_agent_output_detailed(logger: logging.Logger, agent_name: str, output_text: str, output_type: str = "RESPONSE"):
    """Log detailed agent output with醒目 formatting."""
    logger.info(f"{Colors.BOLD}{Colors.OKGREEN}{'✨ AGENT OUTPUT - ' + agent_name.upper() + ' ✨'}{Colors.ENDC}")
    logger.info(f"{Colors.BOLD}{Colors.OKGREEN}{'='*80}{Colors.ENDC}")

    # Log output type
    logger.info(f"{Colors.OKBLUE}📤 TYPE: {output_type}{Colors.ENDC}")

    # Log output content
    logger.info(f"{Colors.OKBLUE}📄 CONTENT:{Colors.ENDC}")
    if len(output_text) > 1000:
        logger.info(f"{Colors.OKGREEN}{output_text[:1000]}...[truncated]{Colors.ENDC}")
    else:
        logger.info(f"{Colors.OKGREEN}{output_text}{Colors.ENDC}")

    logger.info(f"{Colors.BOLD}{Colors.OKGREEN}{'='*80}{Colors.ENDC}")


def log_tool_call(logger: logging.Logger, tool_name: str, args: dict = None, result: str = None):
    """Log tool call with detailed input/output."""
    logger.info(f"{Colors.WARNING}🔧 TOOL CALL: {tool_name}{Colors.ENDC}")

    if args:
        logger.info(f"{Colors.OKCYAN}  📥 INPUT: {args}{Colors.ENDC}")

    if result:
        if len(result) > 300:
            logger.info(f"{Colors.OKGREEN}  📤 OUTPUT: {result[:300]}...[truncated]{Colors.ENDC}")
        else:
            logger.info(f"{Colors.OKGREEN}  📤 OUTPUT: {result}{Colors.ENDC}")

    logger.info(f"{Colors.WARNING}{'─'*60}{Colors.ENDC}")


def log_agent_event(logger: logging.Logger, agent_name: str, event_type: str, event_content: str):
    """Log individual agent events during execution."""
    logger.info(f"{Colors.OKCYAN}⚡ EVENT: {agent_name} - {event_type}{Colors.ENDC}")

    if event_content:
        if len(event_content) > 200:
            logger.info(f"{Colors.OKCYAN}  📋 {event_content[:200]}...[truncated]{Colors.ENDC}")
        else:
            logger.info(f"{Colors.OKCYAN}  📋 {event_content}{Colors.ENDC}")


def log_analysis_complete(logger: logging.Logger, duration: float, success: bool):
    """Log analysis completion."""
    if success:
        logger.info(f"{Colors.OKGREEN}{'='*60}{Colors.ENDC}")
        logger.info(f"{Colors.OKGREEN}✨ Analysis completed successfully in {duration:.2f}s{Colors.ENDC}")
        logger.info(f"{Colors.OKGREEN}{'='*60}{Colors.ENDC}")
    else:
        logger.error(f"{Colors.FAIL}{'='*60}{Colors.ENDC}")
        logger.error(f"{Colors.FAIL}❌ Analysis failed after {duration:.2f}s{Colors.ENDC}")
        logger.error(f"{Colors.FAIL}{'='*60}{Colors.ENDC}")


# Create default logger instance
default_logger = setup_logger(
    name="product_scout",
    level=logging.INFO,
    log_file=Path("logs/product_scout.log"),
    console=True
)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger instance.

    Args:
        name: Optional logger name, defaults to product_scout

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"product_scout.{name}")
    return default_logger
