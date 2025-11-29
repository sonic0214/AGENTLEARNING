"""
Tests for config/prompts.py
"""
import pytest


class TestPrompts:
    """Test cases for prompt templates."""

    def test_prompts_are_non_empty(self):
        """Test that all prompt templates are non-empty."""
        from src.config.prompts import (
            TREND_AGENT_INSTRUCTION,
            MARKET_AGENT_INSTRUCTION,
            COMPETITION_AGENT_INSTRUCTION,
            PROFIT_AGENT_INSTRUCTION,
            EVALUATOR_AGENT_INSTRUCTION,
            REPORT_AGENT_INSTRUCTION,
            ORCHESTRATOR_INSTRUCTION,
        )

        prompts = [
            TREND_AGENT_INSTRUCTION,
            MARKET_AGENT_INSTRUCTION,
            COMPETITION_AGENT_INSTRUCTION,
            PROFIT_AGENT_INSTRUCTION,
            EVALUATOR_AGENT_INSTRUCTION,
            REPORT_AGENT_INSTRUCTION,
            ORCHESTRATOR_INSTRUCTION,
        ]

        for prompt in prompts:
            assert prompt is not None
            assert len(prompt.strip()) > 0
            assert len(prompt) > 100  # Should have substantial content

    def test_prompts_contain_category_placeholder(self):
        """Test that relevant prompts contain {category} placeholder."""
        from src.config.prompts import (
            TREND_AGENT_INSTRUCTION,
            MARKET_AGENT_INSTRUCTION,
            COMPETITION_AGENT_INSTRUCTION,
            PROFIT_AGENT_INSTRUCTION,
        )

        prompts_with_category = [
            TREND_AGENT_INSTRUCTION,
            MARKET_AGENT_INSTRUCTION,
            COMPETITION_AGENT_INSTRUCTION,
            PROFIT_AGENT_INSTRUCTION,
        ]

        for prompt in prompts_with_category:
            assert "{category}" in prompt, "Prompt should contain {category} placeholder"

    def test_prompts_contain_target_market_placeholder(self):
        """Test that relevant prompts contain {target_market} placeholder."""
        from src.config.prompts import (
            TREND_AGENT_INSTRUCTION,
            MARKET_AGENT_INSTRUCTION,
            COMPETITION_AGENT_INSTRUCTION,
            PROFIT_AGENT_INSTRUCTION,
        )

        for prompt in [
            TREND_AGENT_INSTRUCTION,
            MARKET_AGENT_INSTRUCTION,
            COMPETITION_AGENT_INSTRUCTION,
            PROFIT_AGENT_INSTRUCTION,
        ]:
            assert "{target_market}" in prompt

    def test_evaluator_prompt_contains_analysis_placeholders(self):
        """Test that evaluator prompt references other analysis results."""
        from src.config.prompts import EVALUATOR_AGENT_INSTRUCTION

        assert "{trend_analysis}" in EVALUATOR_AGENT_INSTRUCTION
        assert "{market_analysis}" in EVALUATOR_AGENT_INSTRUCTION
        assert "{competition_analysis}" in EVALUATOR_AGENT_INSTRUCTION
        assert "{profit_analysis}" in EVALUATOR_AGENT_INSTRUCTION

    def test_report_prompt_contains_all_placeholders(self):
        """Test that report prompt references all analysis results."""
        from src.config.prompts import REPORT_AGENT_INSTRUCTION

        assert "{category}" in REPORT_AGENT_INSTRUCTION
        assert "{trend_analysis}" in REPORT_AGENT_INSTRUCTION
        assert "{evaluation_result}" in REPORT_AGENT_INSTRUCTION

    def test_format_prompt_basic(self):
        """Test basic prompt formatting."""
        from src.config.prompts import format_prompt

        template = "Analyze {category} in {target_market}"
        result = format_prompt(template, category="laptops", target_market="US")

        assert result == "Analyze laptops in US"

    def test_format_prompt_missing_key(self):
        """Test that missing keys are preserved as placeholders."""
        from src.config.prompts import format_prompt

        template = "Analyze {category} with {missing_key}"
        result = format_prompt(template, category="laptops")

        assert result == "Analyze laptops with {missing_key}"

    def test_format_prompt_extra_keys_ignored(self):
        """Test that extra keys are ignored."""
        from src.config.prompts import format_prompt

        template = "Analyze {category}"
        result = format_prompt(template, category="laptops", extra="ignored")

        assert result == "Analyze laptops"

    def test_get_all_prompts(self):
        """Test that get_all_prompts returns all prompts."""
        from src.config.prompts import get_all_prompts

        prompts = get_all_prompts()

        assert isinstance(prompts, dict)
        assert len(prompts) >= 6
        assert "TREND_AGENT_INSTRUCTION" in prompts
        assert "MARKET_AGENT_INSTRUCTION" in prompts
        assert "COMPETITION_AGENT_INSTRUCTION" in prompts
        assert "PROFIT_AGENT_INSTRUCTION" in prompts
        assert "EVALUATOR_AGENT_INSTRUCTION" in prompts
        assert "REPORT_AGENT_INSTRUCTION" in prompts

    def test_validate_prompts(self):
        """Test prompt validation."""
        from src.config.prompts import validate_prompts

        results = validate_prompts()

        assert isinstance(results, dict)
        # All prompts should be valid
        for name, is_valid in results.items():
            assert is_valid, f"Prompt {name} failed validation"

    def test_prompts_contain_output_format(self):
        """Test that analysis prompts specify output format."""
        from src.config.prompts import (
            TREND_AGENT_INSTRUCTION,
            MARKET_AGENT_INSTRUCTION,
            COMPETITION_AGENT_INSTRUCTION,
            PROFIT_AGENT_INSTRUCTION,
        )

        for prompt in [
            TREND_AGENT_INSTRUCTION,
            MARKET_AGENT_INSTRUCTION,
            COMPETITION_AGENT_INSTRUCTION,
            PROFIT_AGENT_INSTRUCTION,
        ]:
            # Should mention JSON or structured output
            assert "JSON" in prompt or "Output Format" in prompt
