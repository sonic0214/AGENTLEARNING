"""
History service for ProductScout AI.

This module provides services for managing analysis history
and retrieving past results.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid
import os
from pathlib import Path

from src.schemas.input_schemas import AnalysisRequest
from src.schemas.state_schemas import AnalysisState
from src.workflows.analysis_pipeline import PipelineResult


@dataclass
class HistoryServiceConfig:
    """
    Configuration for the history service.

    Attributes:
        max_entries: Maximum history entries to store
        persist_to_file: Whether to persist history to file
        history_file_path: Path for history file
    """
    max_entries: int = 100
    persist_to_file: bool = True
    history_file_path: str = "data/analysis_history.json"


@dataclass
class ServiceHistoryEntry:
    """
    A history entry for the service layer.

    Attributes:
        request: Original analysis request
        state: Final analysis state
        timestamp: When the analysis was completed
        execution_time: How long the analysis took
        success: Whether the analysis succeeded
    """
    request: Optional[AnalysisRequest] = None
    state: Optional[AnalysisState] = None
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0
    success: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request": self.request.to_dict() if self.request else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "execution_time": self.execution_time,
            "success": self.success
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServiceHistoryEntry":
        """Create from dictionary."""
        request = None
        if data.get("request"):
            request = AnalysisRequest.from_dict(data["request"])

        timestamp = datetime.now()
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])

        return cls(
            request=request,
            timestamp=timestamp,
            execution_time=data.get("execution_time", 0.0),
            success=data.get("success", False)
        )


class HistoryService:
    """
    Service for managing analysis history.

    Provides functionality to store, retrieve, and search
    past analysis results.
    """

    def __init__(self, config: Optional[HistoryServiceConfig] = None):
        """
        Initialize the history service.

        Args:
            config: Service configuration
        """
        self.config = config or HistoryServiceConfig()
        self._history: List[ServiceHistoryEntry] = []

        # Load persisted history if enabled
        if self.config.persist_to_file:
            self._load_history()

    def _load_history(self) -> None:
        """Load history from file."""
        if not self.config.persist_to_file:
            return

        # Ensure directory exists
        history_path = Path(self.config.history_file_path)
        history_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if history_path.exists():
                with open(history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = [
                        ServiceHistoryEntry.from_dict(entry)
                        for entry in data
                    ]
                    print(f"✅ Loaded {len(self._history)} history entries from {history_path}")
            else:
                self._history = []
                print(f"📝 History file {history_path} not found, starting fresh")
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            self._history = []
            print(f"⚠️ Error loading history file {history_path}: {e}")
            print(f"📝 Starting with empty history")

    def _save_history(self) -> None:
        """Save history to file."""
        if not self.config.persist_to_file:
            return

        # Ensure directory exists
        history_path = Path(self.config.history_file_path)
        history_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(
                    [entry.to_dict() for entry in self._history],
                    f,
                    indent=2,
                    default=str,
                    ensure_ascii=False
                )
            print(f"💾 Saved {len(self._history)} history entries to {history_path}")
        except IOError as e:
            print(f"⚠️ Error saving history file {history_path}: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error saving history: {e}")

    def add_entry(
        self,
        request: AnalysisRequest,
        result: PipelineResult
    ) -> ServiceHistoryEntry:
        """
        Add a new history entry.

        Args:
            request: Original analysis request
            result: Analysis result

        Returns:
            Created history entry
        """
        entry = ServiceHistoryEntry(
            request=request,
            state=result.state,
            timestamp=datetime.now(),
            execution_time=result.execution_time,
            success=result.success
        )

        self._history.append(entry)

        # Trim to max entries
        if len(self._history) > self.config.max_entries:
            self._history = self._history[-self.config.max_entries:]

        self._save_history()
        return entry

    def get_recent(self, limit: int = 10) -> List[ServiceHistoryEntry]:
        """
        Get recent history entries.

        Args:
            limit: Maximum entries to return

        Returns:
            List of recent history entries
        """
        return list(reversed(self._history[-limit:]))

    def get_by_category(self, category: str) -> List[ServiceHistoryEntry]:
        """
        Get history entries for a specific category.

        Args:
            category: Product category to filter by

        Returns:
            List of matching history entries
        """
        return [
            entry for entry in self._history
            if entry.request and entry.request.category.lower() == category.lower()
        ]

    def get_by_market(self, market: str) -> List[ServiceHistoryEntry]:
        """
        Get history entries for a specific market.

        Args:
            market: Target market to filter by

        Returns:
            List of matching history entries
        """
        return [
            entry for entry in self._history
            if entry.request and entry.request.target_market.upper() == market.upper()
        ]

    def get_successful(self) -> List[ServiceHistoryEntry]:
        """
        Get all successful analysis entries.

        Returns:
            List of successful history entries
        """
        return [entry for entry in self._history if entry.success]

    def get_failed(self) -> List[ServiceHistoryEntry]:
        """
        Get all failed analysis entries.

        Returns:
            List of failed history entries
        """
        return [entry for entry in self._history if not entry.success]

    def search(
        self,
        category: Optional[str] = None,
        market: Optional[str] = None,
        success_only: bool = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ServiceHistoryEntry]:
        """
        Search history with multiple filters.

        Args:
            category: Filter by category (partial match)
            market: Filter by market
            success_only: Only return successful analyses
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            List of matching history entries
        """
        results = self._history.copy()

        if category:
            results = [
                e for e in results
                if e.request and category.lower() in e.request.category.lower()
            ]

        if market:
            results = [
                e for e in results
                if e.request and e.request.target_market.upper() == market.upper()
            ]

        if success_only:
            results = [e for e in results if e.success]

        if start_date:
            results = [e for e in results if e.timestamp >= start_date]

        if end_date:
            results = [e for e in results if e.timestamp <= end_date]

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get history statistics.

        Returns:
            Dictionary with statistics
        """
        total = len(self._history)
        successful = len([e for e in self._history if e.success])
        failed = total - successful

        # Calculate average execution time for successful analyses
        successful_entries = [e for e in self._history if e.success]
        avg_time = 0.0
        if successful_entries:
            avg_time = sum(e.execution_time for e in successful_entries) / len(successful_entries)

        # Get category distribution
        categories: Dict[str, int] = {}
        for entry in self._history:
            if entry.request:
                cat = entry.request.category
                categories[cat] = categories.get(cat, 0) + 1

        # Get market distribution
        markets: Dict[str, int] = {}
        for entry in self._history:
            if entry.request:
                market = entry.request.target_market
                markets[market] = markets.get(market, 0) + 1

        return {
            "total_analyses": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0.0,
            "average_execution_time": avg_time,
            "categories": categories,
            "markets": markets
        }

    def clear(self) -> int:
        """
        Clear all history.

        Returns:
            Number of entries cleared
        """
        count = len(self._history)
        self._history = []
        self._save_history()
        return count

    def get_count(self) -> int:
        """Get total history count."""
        return len(self._history)


def create_history_service(
    config: Optional[HistoryServiceConfig] = None
) -> HistoryService:
    """
    Factory function to create a history service.

    Args:
        config: Service configuration

    Returns:
        Configured HistoryService
    """
    return HistoryService(config)
