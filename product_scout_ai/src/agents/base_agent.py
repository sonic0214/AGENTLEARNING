"""
Base agent module providing common agent functionality.

This module defines the base agent class and common utilities
used by all specialized analysis agents.
"""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from src.config.settings import Settings
from src.config.prompts import format_prompt
from src.utils.logger import log_agent_input_detailed, get_logger, log_tool_call


@dataclass
class AgentConfig:
    """
    Configuration for an agent.

    Attributes:
        name: Agent identifier
        description: Human-readable description
        instruction_template: Prompt template for the agent
        tools: List of tools available to the agent
        model_name: LLM model to use
        output_key: Key for storing output in session state
    """
    name: str
    description: str
    instruction_template: str
    tools: Optional[List[Any]] = None
    model_name: Optional[str] = None
    output_key: Optional[str] = None


class BaseAnalysisAgent:
    """
    Base class for all analysis agents.

    Provides common functionality for creating and running ADK agents.
    """

    def __init__(self, config: AgentConfig, settings: Optional[Settings] = None):
        """
        Initialize the agent.

        Args:
            config: Agent configuration
            settings: Application settings (uses defaults if not provided)
        """
        self.config = config
        self.settings = settings or Settings()
        self._agent: Optional[LlmAgent] = None

    @property
    def name(self) -> str:
        """Get agent name."""
        return self.config.name

    @property
    def description(self) -> str:
        """Get agent description."""
        return self.config.description

    def create_agent(self, **format_kwargs) -> LlmAgent:
        """
        Create the ADK LlmAgent instance.

        Args:
            **format_kwargs: Keyword arguments for formatting the instruction template

        Returns:
            Configured LlmAgent instance
        """
        # Format the instruction with provided kwargs
        instruction = format_prompt(
            self.config.instruction_template,
            **format_kwargs
        )

        # Build tools list
        tools = self.config.tools or []
        if google_search not in tools:
            tools = [google_search] + tools

        # Log agent creation with detailed input
        log_agent_input_detailed(
            logger=get_logger(self.config.name),
            agent_name=self.config.name,
            instruction=instruction,
            tools=tools
        )

        # Create the agent
        self._agent = LlmAgent(
            name=self.config.name,
            model=self.config.model_name or self.settings.MODEL_NAME,
            instruction=instruction,
            description=self.config.description,
            tools=tools,
        )

        return self._agent

    def get_agent(self) -> Optional[LlmAgent]:
        """
        Get the created agent instance.

        Returns:
            The LlmAgent instance or None if not created
        """
        return self._agent

    def get_output_key(self) -> str:
        """
        Get the session state key for this agent's output.

        Returns:
            Output key string
        """
        return self.config.output_key or f"{self.config.name}_result"


def create_analysis_agent(
    name: str,
    description: str,
    instruction_template: str,
    tools: Optional[List[Any]] = None,
    model_name: Optional[str] = None,
    output_key: Optional[str] = None,
    settings: Optional[Settings] = None,
    **format_kwargs
) -> LlmAgent:
    """
    Factory function to create an analysis agent.

    This is a convenience function for creating agents without
    using the class-based approach.

    Args:
        name: Agent identifier
        description: Human-readable description
        instruction_template: Prompt template
        tools: Available tools
        model_name: LLM model name
        output_key: Session state output key
        settings: Application settings
        **format_kwargs: Template formatting arguments

    Returns:
        Configured LlmAgent instance
    """
    config = AgentConfig(
        name=name,
        description=description,
        instruction_template=instruction_template,
        tools=tools,
        model_name=model_name,
        output_key=output_key
    )

    agent = BaseAnalysisAgent(config, settings)
    return agent.create_agent(**format_kwargs)


def validate_agent_output(output: Any, required_fields: List[str]) -> bool:
    """
    Validate that agent output contains required fields.

    Args:
        output: Agent output (typically a dict)
        required_fields: List of required field names

    Returns:
        True if all required fields present, False otherwise
    """
    if not isinstance(output, dict):
        return False

    for field in required_fields:
        if field not in output:
            return False

    return True


def extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from an agent response that may contain markdown.

    Args:
        response: Raw response string

    Returns:
        Parsed JSON dict or None if not found
    """
    import json
    import re

    # Try to find JSON in code blocks
    json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    matches = re.findall(json_pattern, response)

    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue

    # Try to parse the whole response as JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in response
    brace_pattern = r'\{[\s\S]*\}'
    brace_matches = re.findall(brace_pattern, response)

    for match in brace_matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    return None
