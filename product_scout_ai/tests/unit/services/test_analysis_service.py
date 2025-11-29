"""
Tests for services/analysis_service.py
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.services.analysis_service import (
    AnalysisService,
    AnalysisServiceConfig,
    create_analysis_service,
    quick_analysis,
)
from src.schemas.input_schemas import AnalysisRequest
from src.schemas.state_schemas import AnalysisState
from src.workflows.analysis_pipeline import PipelineResult
from src.config.settings import Settings


class TestAnalysisServiceConfig:
    """Test cases for AnalysisServiceConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = AnalysisServiceConfig()

        assert config.enable_caching is False
        assert config.cache_ttl_seconds == 3600
        assert config.max_concurrent_analyses == 5
        assert config.default_timeout_seconds == 300

    def test_custom_values(self):
        """Test custom configuration values."""
        config = AnalysisServiceConfig(
            enable_caching=True,
            cache_ttl_seconds=7200,
            max_concurrent_analyses=10,
            default_timeout_seconds=600
        )

        assert config.enable_caching is True
        assert config.cache_ttl_seconds == 7200
        assert config.max_concurrent_analyses == 10
        assert config.default_timeout_seconds == 600


class TestAnalysisService:
    """Test cases for AnalysisService."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    @pytest.fixture
    def sample_request(self):
        """Create sample request."""
        return AnalysisRequest(
            category="portable blender",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba"
        )

    @pytest.fixture
    def mock_result(self):
        """Create mock pipeline result."""
        return PipelineResult(
            success=True,
            state=AnalysisState(),
            execution_time=5.0
        )

    @patch('src.services.analysis_service.PipelineRunner')
    def test_service_initialization(self, mock_runner_class, mock_settings):
        """Test service initialization."""
        service = AnalysisService(settings=mock_settings)

        assert service.settings == mock_settings
        assert service.config is not None
        mock_runner_class.assert_called_once()

    @patch('src.services.analysis_service.PipelineRunner')
    def test_service_initialization_with_config(self, mock_runner_class):
        """Test service initialization with config."""
        config = AnalysisServiceConfig(max_concurrent_analyses=3)
        service = AnalysisService(config=config)

        assert service.config.max_concurrent_analyses == 3

    @patch('src.services.analysis_service.PipelineRunner')
    def test_get_cache_key(self, mock_runner_class, sample_request):
        """Test cache key generation."""
        service = AnalysisService()
        key = service._get_cache_key(sample_request)

        assert "portable blender" in key
        assert "US" in key
        assert "amazon_fba" in key
        assert "medium" in key

    @patch('src.services.analysis_service.PipelineRunner')
    def test_cache_disabled_by_default(self, mock_runner_class, sample_request):
        """Test cache is disabled by default."""
        service = AnalysisService()

        result = service._get_cached_result(sample_request)
        assert result is None

    @patch('src.services.analysis_service.PipelineRunner')
    def test_cache_stores_result(self, mock_runner_class, sample_request, mock_result):
        """Test caching stores result when enabled."""
        config = AnalysisServiceConfig(enable_caching=True)
        service = AnalysisService(config=config)

        service._cache_result(sample_request, mock_result)

        cached = service._get_cached_result(sample_request)
        assert cached is not None
        assert cached.success is True

    @patch('src.services.analysis_service.PipelineRunner')
    def test_cache_not_stored_when_disabled(self, mock_runner_class, sample_request, mock_result):
        """Test caching does not store when disabled."""
        service = AnalysisService()

        service._cache_result(sample_request, mock_result)

        cached = service._get_cached_result(sample_request)
        assert cached is None

    @pytest.mark.asyncio
    @patch('src.services.analysis_service.PipelineRunner')
    async def test_analyze_success(self, mock_runner_class, sample_request, mock_result):
        """Test successful analysis."""
        mock_runner = Mock()
        mock_runner.run_analysis = AsyncMock(return_value=mock_result)
        mock_runner.initialize_pipeline = Mock()
        mock_runner.create_session = Mock()
        mock_runner_class.return_value = mock_runner

        service = AnalysisService()
        result = await service.analyze(sample_request)

        assert result.success is True
        mock_runner.run_analysis.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.services.analysis_service.PipelineRunner')
    async def test_analyze_returns_cached(self, mock_runner_class, sample_request, mock_result):
        """Test analyze returns cached result."""
        mock_runner = Mock()
        mock_runner.run_analysis = AsyncMock(return_value=mock_result)
        mock_runner.initialize_pipeline = Mock()
        mock_runner.create_session = Mock()
        mock_runner_class.return_value = mock_runner

        config = AnalysisServiceConfig(enable_caching=True)
        service = AnalysisService(config=config)

        # First call
        result1 = await service.analyze(sample_request)
        # Second call should use cache
        result2 = await service.analyze(sample_request)

        # Runner should only be called once
        assert mock_runner.run_analysis.call_count == 1
        assert result1.success == result2.success

    @pytest.mark.asyncio
    @patch('src.services.analysis_service.PipelineRunner')
    async def test_analyze_with_progress_callback(self, mock_runner_class, sample_request, mock_result):
        """Test analyze with progress callback."""
        mock_runner = Mock()
        mock_runner.run_analysis = AsyncMock(return_value=mock_result)
        mock_runner.initialize_pipeline = Mock()
        mock_runner.create_session = Mock()
        mock_runner_class.return_value = mock_runner

        service = AnalysisService()
        callback = Mock()

        result = await service.analyze(sample_request, on_progress=callback)

        mock_runner.initialize_pipeline.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.services.analysis_service.PipelineRunner')
    async def test_analyze_with_streaming(self, mock_runner_class, sample_request):
        """Test streaming analysis."""
        mock_runner = Mock()

        async def mock_streaming(req):
            yield {"type": "started", "phase": "initialized"}
            yield {"type": "completed", "phase": "completed"}

        mock_runner.run_with_streaming = mock_streaming
        mock_runner.initialize_pipeline = Mock()
        mock_runner_class.return_value = mock_runner

        service = AnalysisService()

        updates = []
        async for update in service.analyze_with_streaming(sample_request):
            updates.append(update)

        assert len(updates) == 2
        assert updates[0]["type"] == "started"
        assert updates[-1]["type"] == "completed"

    @patch('src.services.analysis_service.PipelineRunner')
    def test_get_active_analyses(self, mock_runner_class):
        """Test getting active analyses."""
        service = AnalysisService()

        active = service.get_active_analyses()
        assert isinstance(active, dict)
        assert len(active) == 0

    @patch('src.services.analysis_service.PipelineRunner')
    def test_get_active_count(self, mock_runner_class):
        """Test getting active count."""
        service = AnalysisService()

        count = service.get_active_count()
        assert count == 0

    @patch('src.services.analysis_service.PipelineRunner')
    def test_get_available_slots(self, mock_runner_class):
        """Test getting available slots."""
        config = AnalysisServiceConfig(max_concurrent_analyses=5)
        service = AnalysisService(config=config)

        slots = service.get_available_slots()
        assert slots == 5

    @patch('src.services.analysis_service.PipelineRunner')
    def test_clear_cache(self, mock_runner_class, sample_request, mock_result):
        """Test clearing cache."""
        config = AnalysisServiceConfig(enable_caching=True)
        service = AnalysisService(config=config)

        service._cache_result(sample_request, mock_result)
        count = service.clear_cache()

        assert count == 1
        assert len(service._cache) == 0

    @patch('src.services.analysis_service.PipelineRunner')
    def test_get_cache_stats(self, mock_runner_class, sample_request, mock_result):
        """Test getting cache stats."""
        config = AnalysisServiceConfig(enable_caching=True, cache_ttl_seconds=7200)
        service = AnalysisService(config=config)

        service._cache_result(sample_request, mock_result)
        stats = service.get_cache_stats()

        assert stats["enabled"] is True
        assert stats["entries"] == 1
        assert stats["ttl_seconds"] == 7200


class TestCreateAnalysisService:
    """Test cases for create_analysis_service function."""

    @patch('src.services.analysis_service.PipelineRunner')
    def test_create_service_default(self, mock_runner_class):
        """Test creating service with defaults."""
        service = create_analysis_service()

        assert isinstance(service, AnalysisService)

    @patch('src.services.analysis_service.PipelineRunner')
    def test_create_service_with_settings(self, mock_runner_class):
        """Test creating service with settings."""
        settings = Mock(spec=Settings)
        service = create_analysis_service(settings=settings)

        assert service.settings == settings

    @patch('src.services.analysis_service.PipelineRunner')
    def test_create_service_with_config(self, mock_runner_class):
        """Test creating service with config."""
        config = AnalysisServiceConfig(enable_caching=True)
        service = create_analysis_service(config=config)

        assert service.config.enable_caching is True


class TestQuickAnalysis:
    """Test cases for quick_analysis function."""

    @pytest.mark.asyncio
    @patch('src.services.analysis_service.create_analysis_service')
    async def test_quick_analysis_default_params(self, mock_create_service):
        """Test quick_analysis with default parameters."""
        mock_service = Mock()
        mock_result = PipelineResult(
            success=True,
            state=AnalysisState(),
            execution_time=5.0
        )
        mock_service.analyze = AsyncMock(return_value=mock_result)
        mock_create_service.return_value = mock_service

        result = await quick_analysis("portable blender")

        mock_service.analyze.assert_called_once()
        call_args = mock_service.analyze.call_args[0][0]
        assert call_args.category == "portable blender"
        assert call_args.target_market == "US"

    @pytest.mark.asyncio
    @patch('src.services.analysis_service.create_analysis_service')
    async def test_quick_analysis_custom_params(self, mock_create_service):
        """Test quick_analysis with custom parameters."""
        mock_service = Mock()
        mock_result = PipelineResult(
            success=True,
            state=AnalysisState(),
            execution_time=5.0
        )
        mock_service.analyze = AsyncMock(return_value=mock_result)
        mock_create_service.return_value = mock_service

        result = await quick_analysis(
            "smart watch",
            target_market="EU",
            business_model="dropshipping"
        )

        call_args = mock_service.analyze.call_args[0][0]
        assert call_args.category == "smart watch"
        assert call_args.target_market == "EU"
        assert call_args.business_model == "dropshipping"
