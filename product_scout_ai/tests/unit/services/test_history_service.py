"""
Tests for services/history_service.py
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import tempfile
import os

from src.services.history_service import (
    HistoryService,
    HistoryServiceConfig,
    ServiceHistoryEntry,
    create_history_service,
)
from src.schemas.input_schemas import AnalysisRequest
from src.schemas.state_schemas import AnalysisState
from src.workflows.analysis_pipeline import PipelineResult


class TestHistoryServiceConfig:
    """Test cases for HistoryServiceConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = HistoryServiceConfig()

        assert config.max_entries == 100
        assert config.persist_to_file is False
        assert config.history_file_path == "analysis_history.json"

    def test_custom_values(self):
        """Test custom configuration values."""
        config = HistoryServiceConfig(
            max_entries=50,
            persist_to_file=True,
            history_file_path="/tmp/history.json"
        )

        assert config.max_entries == 50
        assert config.persist_to_file is True
        assert config.history_file_path == "/tmp/history.json"


class TestHistoryService:
    """Test cases for HistoryService."""

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
    def sample_result(self):
        """Create sample pipeline result."""
        return PipelineResult(
            success=True,
            state=AnalysisState(),
            execution_time=5.0
        )

    @pytest.fixture
    def failed_result(self):
        """Create failed pipeline result."""
        return PipelineResult(
            success=False,
            state=AnalysisState(),
            error="Test error",
            execution_time=1.0
        )

    def test_service_initialization(self):
        """Test service initialization."""
        service = HistoryService()

        assert service.config is not None
        assert len(service._history) == 0

    def test_service_initialization_with_config(self):
        """Test service initialization with config."""
        config = HistoryServiceConfig(max_entries=50)
        service = HistoryService(config=config)

        assert service.config.max_entries == 50

    def test_add_entry(self, sample_request, sample_result):
        """Test adding history entry."""
        service = HistoryService()

        entry = service.add_entry(sample_request, sample_result)

        assert entry is not None
        assert entry.request == sample_request
        assert entry.success is True
        assert service.get_count() == 1

    def test_add_multiple_entries(self, sample_request, sample_result):
        """Test adding multiple entries."""
        service = HistoryService()

        service.add_entry(sample_request, sample_result)
        service.add_entry(sample_request, sample_result)
        service.add_entry(sample_request, sample_result)

        assert service.get_count() == 3

    def test_max_entries_limit(self, sample_request, sample_result):
        """Test max entries limit is respected."""
        config = HistoryServiceConfig(max_entries=3)
        service = HistoryService(config=config)

        for _ in range(5):
            service.add_entry(sample_request, sample_result)

        assert service.get_count() == 3

    def test_get_recent(self, sample_request, sample_result):
        """Test getting recent entries."""
        service = HistoryService()

        for i in range(5):
            service.add_entry(sample_request, sample_result)

        recent = service.get_recent(limit=3)

        assert len(recent) == 3

    def test_get_recent_fewer_entries(self, sample_request, sample_result):
        """Test get_recent with fewer entries than limit."""
        service = HistoryService()

        service.add_entry(sample_request, sample_result)
        service.add_entry(sample_request, sample_result)

        recent = service.get_recent(limit=5)

        assert len(recent) == 2

    def test_get_by_category(self, sample_result):
        """Test getting entries by category."""
        service = HistoryService()

        req1 = AnalysisRequest(category="blender", target_market="US")
        req2 = AnalysisRequest(category="watch", target_market="US")
        req3 = AnalysisRequest(category="blender", target_market="EU")

        service.add_entry(req1, sample_result)
        service.add_entry(req2, sample_result)
        service.add_entry(req3, sample_result)

        blender_entries = service.get_by_category("blender")
        assert len(blender_entries) == 2

        watch_entries = service.get_by_category("watch")
        assert len(watch_entries) == 1

    def test_get_by_category_case_insensitive(self, sample_result):
        """Test category search is case insensitive."""
        service = HistoryService()

        req = AnalysisRequest(category="Portable Blender", target_market="US")
        service.add_entry(req, sample_result)

        entries = service.get_by_category("portable blender")
        assert len(entries) == 1

    def test_get_by_market(self, sample_result):
        """Test getting entries by market."""
        service = HistoryService()

        req1 = AnalysisRequest(category="blender", target_market="US")
        req2 = AnalysisRequest(category="watch", target_market="EU")
        req3 = AnalysisRequest(category="phone", target_market="US")

        service.add_entry(req1, sample_result)
        service.add_entry(req2, sample_result)
        service.add_entry(req3, sample_result)

        us_entries = service.get_by_market("US")
        assert len(us_entries) == 2

        eu_entries = service.get_by_market("EU")
        assert len(eu_entries) == 1

    def test_get_successful(self, sample_request, sample_result, failed_result):
        """Test getting successful entries."""
        service = HistoryService()

        service.add_entry(sample_request, sample_result)
        service.add_entry(sample_request, failed_result)
        service.add_entry(sample_request, sample_result)

        successful = service.get_successful()
        assert len(successful) == 2

    def test_get_failed(self, sample_request, sample_result, failed_result):
        """Test getting failed entries."""
        service = HistoryService()

        service.add_entry(sample_request, sample_result)
        service.add_entry(sample_request, failed_result)
        service.add_entry(sample_request, failed_result)

        failed = service.get_failed()
        assert len(failed) == 2

    def test_search_by_category(self, sample_result):
        """Test search with category filter."""
        service = HistoryService()

        req1 = AnalysisRequest(category="portable blender", target_market="US")
        req2 = AnalysisRequest(category="smart watch", target_market="US")

        service.add_entry(req1, sample_result)
        service.add_entry(req2, sample_result)

        results = service.search(category="blender")
        assert len(results) == 1

    def test_search_by_market(self, sample_result):
        """Test search with market filter."""
        service = HistoryService()

        req1 = AnalysisRequest(category="blender", target_market="US")
        req2 = AnalysisRequest(category="watch", target_market="EU")

        service.add_entry(req1, sample_result)
        service.add_entry(req2, sample_result)

        results = service.search(market="EU")
        assert len(results) == 1

    def test_search_success_only(self, sample_request, sample_result, failed_result):
        """Test search with success_only filter."""
        service = HistoryService()

        service.add_entry(sample_request, sample_result)
        service.add_entry(sample_request, failed_result)

        results = service.search(success_only=True)
        assert len(results) == 1

    def test_search_multiple_filters(self, sample_result, failed_result):
        """Test search with multiple filters."""
        service = HistoryService()

        req1 = AnalysisRequest(category="blender", target_market="US")
        req2 = AnalysisRequest(category="blender", target_market="EU")

        service.add_entry(req1, sample_result)
        service.add_entry(req2, failed_result)

        results = service.search(category="blender", market="US", success_only=True)
        assert len(results) == 1

    def test_get_statistics_empty(self):
        """Test statistics with no entries."""
        service = HistoryService()

        stats = service.get_statistics()

        assert stats["total_analyses"] == 0
        assert stats["successful"] == 0
        assert stats["failed"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["average_execution_time"] == 0.0

    def test_get_statistics_with_entries(self, sample_request, sample_result, failed_result):
        """Test statistics with entries."""
        service = HistoryService()

        service.add_entry(sample_request, sample_result)
        service.add_entry(sample_request, sample_result)
        service.add_entry(sample_request, failed_result)

        stats = service.get_statistics()

        assert stats["total_analyses"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == pytest.approx(0.667, rel=0.01)
        assert stats["average_execution_time"] == 5.0

    def test_get_statistics_category_distribution(self, sample_result):
        """Test category distribution in statistics."""
        service = HistoryService()

        req1 = AnalysisRequest(category="blender", target_market="US")
        req2 = AnalysisRequest(category="watch", target_market="US")
        req3 = AnalysisRequest(category="blender", target_market="EU")

        service.add_entry(req1, sample_result)
        service.add_entry(req2, sample_result)
        service.add_entry(req3, sample_result)

        stats = service.get_statistics()

        assert stats["categories"]["blender"] == 2
        assert stats["categories"]["watch"] == 1

    def test_get_statistics_market_distribution(self, sample_result):
        """Test market distribution in statistics."""
        service = HistoryService()

        req1 = AnalysisRequest(category="blender", target_market="US")
        req2 = AnalysisRequest(category="watch", target_market="EU")
        req3 = AnalysisRequest(category="phone", target_market="US")

        service.add_entry(req1, sample_result)
        service.add_entry(req2, sample_result)
        service.add_entry(req3, sample_result)

        stats = service.get_statistics()

        assert stats["markets"]["US"] == 2
        assert stats["markets"]["EU"] == 1

    def test_clear(self, sample_request, sample_result):
        """Test clearing history."""
        service = HistoryService()

        service.add_entry(sample_request, sample_result)
        service.add_entry(sample_request, sample_result)

        count = service.clear()

        assert count == 2
        assert service.get_count() == 0

    def test_get_count(self, sample_request, sample_result):
        """Test getting count."""
        service = HistoryService()

        assert service.get_count() == 0

        service.add_entry(sample_request, sample_result)
        assert service.get_count() == 1


class TestHistoryServicePersistence:
    """Test cases for history persistence."""

    @pytest.fixture
    def temp_file(self):
        """Create temporary file for testing."""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_persistence_saves_on_add(self, temp_file):
        """Test history is saved when entry is added."""
        config = HistoryServiceConfig(
            persist_to_file=True,
            history_file_path=temp_file
        )
        service = HistoryService(config=config)

        req = AnalysisRequest(category="blender", target_market="US")
        result = PipelineResult(success=True, state=AnalysisState(), execution_time=5.0)

        service.add_entry(req, result)

        # Check file exists and has content
        assert os.path.exists(temp_file)
        with open(temp_file, 'r') as f:
            content = f.read()
            assert "blender" in content

    def test_persistence_loads_on_init(self, temp_file):
        """Test history is loaded on initialization."""
        config = HistoryServiceConfig(
            persist_to_file=True,
            history_file_path=temp_file
        )

        # Create and populate first service
        service1 = HistoryService(config=config)
        req = AnalysisRequest(category="blender", target_market="US")
        result = PipelineResult(success=True, state=AnalysisState(), execution_time=5.0)
        service1.add_entry(req, result)

        # Create second service and verify data is loaded
        service2 = HistoryService(config=config)
        assert service2.get_count() == 1

    def test_persistence_handles_missing_file(self, temp_file):
        """Test handling of missing history file."""
        os.unlink(temp_file)  # Remove the file

        config = HistoryServiceConfig(
            persist_to_file=True,
            history_file_path=temp_file
        )
        service = HistoryService(config=config)

        # Should initialize with empty history
        assert service.get_count() == 0


class TestCreateHistoryService:
    """Test cases for create_history_service function."""

    def test_create_service_default(self):
        """Test creating service with defaults."""
        service = create_history_service()

        assert isinstance(service, HistoryService)
        assert service.config.max_entries == 100

    def test_create_service_with_config(self):
        """Test creating service with config."""
        config = HistoryServiceConfig(max_entries=50)
        service = create_history_service(config=config)

        assert service.config.max_entries == 50
