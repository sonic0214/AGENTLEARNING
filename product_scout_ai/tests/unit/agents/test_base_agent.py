"""
Tests for agents/base_agent.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents.base_agent import (
    BaseAnalysisAgent,
    AgentConfig,
    create_analysis_agent,
    validate_agent_output,
    extract_json_from_response,
)
from src.config.settings import Settings


class TestAgentConfig:
    """Test cases for AgentConfig."""

    def test_config_creation(self):
        """Test creating an AgentConfig."""
        config = AgentConfig(
            name="test_agent",
            description="A test agent",
            instruction_template="Analyze {category}"
        )

        assert config.name == "test_agent"
        assert config.description == "A test agent"
        assert config.instruction_template == "Analyze {category}"

    def test_config_with_optional_fields(self):
        """Test config with all optional fields."""
        config = AgentConfig(
            name="test_agent",
            description="Test",
            instruction_template="Template",
            tools=[Mock()],
            model_name="gemini-2.0-pro",
            output_key="custom_output"
        )

        assert config.tools is not None
        assert len(config.tools) == 1
        assert config.model_name == "gemini-2.0-pro"
        assert config.output_key == "custom_output"

    def test_config_defaults(self):
        """Test config default values."""
        config = AgentConfig(
            name="test",
            description="Test",
            instruction_template="Template"
        )

        assert config.tools is None
        assert config.model_name is None
        assert config.output_key is None


class TestBaseAnalysisAgent:
    """Test cases for BaseAnalysisAgent."""

    @pytest.fixture
    def agent_config(self):
        """Create test agent config."""
        return AgentConfig(
            name="test_analysis_agent",
            description="Test analysis agent",
            instruction_template="Analyze {category} in {target_market}",
            output_key="test_output"
        )

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        settings.GOOGLE_API_KEY = "test_key"
        return settings

    def test_agent_initialization(self, agent_config, mock_settings):
        """Test agent initialization."""
        agent = BaseAnalysisAgent(agent_config, mock_settings)

        assert agent.name == "test_analysis_agent"
        assert agent.description == "Test analysis agent"
        assert agent.settings == mock_settings

    def test_agent_name_property(self, agent_config, mock_settings):
        """Test name property."""
        agent = BaseAnalysisAgent(agent_config, mock_settings)

        assert agent.name == agent_config.name

    def test_agent_description_property(self, agent_config, mock_settings):
        """Test description property."""
        agent = BaseAnalysisAgent(agent_config, mock_settings)

        assert agent.description == agent_config.description

    def test_get_output_key(self, agent_config, mock_settings):
        """Test get_output_key method."""
        agent = BaseAnalysisAgent(agent_config, mock_settings)

        assert agent.get_output_key() == "test_output"

    def test_get_output_key_default(self, mock_settings):
        """Test get_output_key with no explicit key."""
        config = AgentConfig(
            name="my_agent",
            description="Test",
            instruction_template="Template"
        )
        agent = BaseAnalysisAgent(config, mock_settings)

        assert agent.get_output_key() == "my_agent_result"

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_agent(self, mock_search, mock_llm_agent, agent_config, mock_settings):
        """Test create_agent method."""
        agent = BaseAnalysisAgent(agent_config, mock_settings)
        llm_agent = agent.create_agent(category="blender", target_market="US")

        mock_llm_agent.assert_called_once()
        call_kwargs = mock_llm_agent.call_args[1]

        assert call_kwargs["name"] == "test_analysis_agent"
        assert call_kwargs["model"] == "gemini-2.0-flash"
        assert "blender" in call_kwargs["instruction"]
        assert "US" in call_kwargs["instruction"]

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_get_agent_returns_created_agent(self, mock_search, mock_llm_agent, agent_config, mock_settings):
        """Test get_agent returns the created agent."""
        agent = BaseAnalysisAgent(agent_config, mock_settings)

        # Before creation
        assert agent.get_agent() is None

        # After creation
        agent.create_agent(category="test", target_market="US")
        assert agent.get_agent() is not None


class TestCreateAnalysisAgent:
    """Test cases for create_analysis_agent factory function."""

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_analysis_agent(self, mock_search, mock_llm_agent):
        """Test factory function creates agent correctly."""
        llm_agent = create_analysis_agent(
            name="factory_agent",
            description="Factory created agent",
            instruction_template="Test {param}",
            param="value"
        )

        mock_llm_agent.assert_called_once()
        call_kwargs = mock_llm_agent.call_args[1]

        assert call_kwargs["name"] == "factory_agent"
        assert "value" in call_kwargs["instruction"]


class TestValidateAgentOutput:
    """Test cases for validate_agent_output."""

    def test_valid_output(self):
        """Test validation with valid output."""
        output = {
            "score": 75,
            "analysis": "Test analysis",
            "recommendation": "go"
        }
        required = ["score", "analysis", "recommendation"]

        assert validate_agent_output(output, required) is True

    def test_missing_field(self):
        """Test validation with missing field."""
        output = {
            "score": 75,
            "analysis": "Test"
        }
        required = ["score", "analysis", "recommendation"]

        assert validate_agent_output(output, required) is False

    def test_non_dict_output(self):
        """Test validation with non-dict output."""
        assert validate_agent_output("string output", ["field"]) is False
        assert validate_agent_output(None, ["field"]) is False
        assert validate_agent_output(123, ["field"]) is False

    def test_empty_required_fields(self):
        """Test validation with no required fields."""
        output = {"any": "data"}

        assert validate_agent_output(output, []) is True

    def test_empty_output(self):
        """Test validation with empty output."""
        assert validate_agent_output({}, ["field"]) is False
        assert validate_agent_output({}, []) is True


class TestExtractJsonFromResponse:
    """Test cases for extract_json_from_response."""

    def test_extract_json_code_block(self):
        """Test extracting JSON from markdown code block."""
        response = '''
        Here is the analysis:

        ```json
        {"score": 75, "recommendation": "go"}
        ```

        That's the result.
        '''
        result = extract_json_from_response(response)

        assert result is not None
        assert result["score"] == 75
        assert result["recommendation"] == "go"

    def test_extract_json_no_language_tag(self):
        """Test extracting JSON from code block without language tag."""
        response = '''
        ```
        {"score": 50}
        ```
        '''
        result = extract_json_from_response(response)

        assert result is not None
        assert result["score"] == 50

    def test_extract_raw_json(self):
        """Test extracting raw JSON string."""
        response = '{"score": 80, "analysis": "test"}'
        result = extract_json_from_response(response)

        assert result is not None
        assert result["score"] == 80

    def test_extract_json_embedded(self):
        """Test extracting JSON embedded in text."""
        response = 'The analysis shows {"score": 65} which is good.'
        result = extract_json_from_response(response)

        assert result is not None
        assert result["score"] == 65

    def test_no_json_found(self):
        """Test when no JSON is present."""
        response = "This is just plain text with no JSON."
        result = extract_json_from_response(response)

        assert result is None

    def test_invalid_json(self):
        """Test with malformed JSON."""
        response = '{"score": invalid}'
        result = extract_json_from_response(response)

        assert result is None

    def test_nested_json(self):
        """Test extracting nested JSON."""
        response = '''
        ```json
        {
            "scores": {
                "trend": 70,
                "market": 65
            },
            "overall": 68
        }
        ```
        '''
        result = extract_json_from_response(response)

        assert result is not None
        assert result["scores"]["trend"] == 70
        assert result["overall"] == 68
