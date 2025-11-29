"""
Analysis service for ProductScout AI.

This module provides the high-level service interface for
running product opportunity analyses.
"""
from typing import Dict, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import asyncio
import time

from src.config.settings import Settings
from src.schemas.input_schemas import AnalysisRequest
from src.schemas.output_schemas import FinalReport
from src.schemas.state_schemas import AnalysisState
from src.workflows.analysis_pipeline import AnalysisPipeline, PipelineResult
from src.workflows.runner import PipelineRunner, RunnerConfig
from src.utils.logger import get_logger, log_analysis_start, log_analysis_complete


@dataclass
class AnalysisServiceConfig:
    """
    Configuration for the analysis service.

    Attributes:
        enable_caching: Enable result caching
        cache_ttl_seconds: Cache time-to-live in seconds
        max_concurrent_analyses: Maximum concurrent analyses
        default_timeout_seconds: Default analysis timeout
    """
    enable_caching: bool = False
    cache_ttl_seconds: int = 3600
    max_concurrent_analyses: int = 5
    default_timeout_seconds: int = 300


class AnalysisService:
    """
    High-level service for product opportunity analysis.

    This service provides a clean interface for running analyses,
    managing state, and handling results.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        config: Optional[AnalysisServiceConfig] = None
    ):
        """
        Initialize the analysis service.

        Args:
            settings: Application settings
            config: Service configuration
        """
        self.settings = settings or Settings()
        self.config = config or AnalysisServiceConfig()
        self.logger = get_logger("analysis_service")

        # Initialize runner
        runner_config = RunnerConfig(
            timeout_seconds=self.config.default_timeout_seconds
        )
        self._runner = PipelineRunner(
            settings=self.settings,
            config=runner_config
        )

        # Analysis tracking
        self._active_analyses: Dict[str, AnalysisState] = {}
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_analyses)

        # Simple result cache
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _get_cache_key(self, request: AnalysisRequest) -> str:
        """Generate cache key for a request."""
        return f"{request.category}:{request.target_market}:{request.business_model}:{request.budget_range}"

    def _get_cached_result(self, request: AnalysisRequest) -> Optional[PipelineResult]:
        """Get cached result if available and not expired."""
        if not self.config.enable_caching:
            return None

        cache_key = self._get_cache_key(request)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            cached_time = cached.get("timestamp", datetime.min)

            if isinstance(cached_time, datetime):
                age = (datetime.now() - cached_time).total_seconds()
                if age < self.config.cache_ttl_seconds:
                    return cached.get("result")

            # Expired, remove from cache
            del self._cache[cache_key]

        return None

    def _cache_result(self, request: AnalysisRequest, result: PipelineResult) -> None:
        """Cache a result."""
        if not self.config.enable_caching:
            return

        cache_key = self._get_cache_key(request)
        self._cache[cache_key] = {
            "result": result,
            "timestamp": datetime.now()
        }

    async def analyze(
        self,
        request: AnalysisRequest,
        on_progress: Optional[Callable[[str, str], None]] = None
    ) -> PipelineResult:
        """
        Run a product opportunity analysis.

        Args:
            request: Analysis request
            on_progress: Optional callback for progress updates (phase, message)

        Returns:
            PipelineResult with analysis results
        """
        start_time = time.time()

        # Log analysis start
        log_analysis_start(self.logger, request.category, request.target_market)

        # Check cache first
        cached_result = self._get_cached_result(request)
        if cached_result:
            self.logger.info("♻️  Using cached result")
            return cached_result

        # Acquire semaphore for concurrency control
        async with self._semaphore:
            self.logger.info(f"🔒 Acquired analysis slot ({self.get_active_count() + 1}/{self.config.max_concurrent_analyses})")

            # Initialize pipeline with progress callback
            if on_progress:
                def phase_callback(phase: str, data: Dict[str, Any]) -> None:
                    message = get_phase_description(phase)
                    self.logger.info(f"📍 Phase update: {phase} - {message}")
                    on_progress(phase, message)

                self._runner.initialize_pipeline(on_phase_complete=phase_callback)
            else:
                self._runner.initialize_pipeline()

            # Create session and run
            session = await self._runner.create_session()
            self.logger.info(f"🔖 Created session: {session.id if hasattr(session, 'id') else 'unknown'}")

            # Track active analysis
            analysis_id = str(session.id) if hasattr(session, 'id') else "unknown"
            state = AnalysisState(request=request)
            self._active_analyses[analysis_id] = state

            try:
                self.logger.info("🏃 Starting analysis pipeline execution...")
                result_obj = await self._runner.run_analysis(request, session)

                duration = time.time() - start_time

                # Handle Result type
                if result_obj.is_ok():
                    # Success case
                    pipeline_result = result_obj.unwrap()
                    log_analysis_complete(self.logger, duration, pipeline_result.success)

                    if pipeline_result.success:
                        self._cache_result(request, pipeline_result)
                        self.logger.info("💾 Result cached successfully")

                    return pipeline_result

                else:
                    # Error case - unwrap error context
                    error_ctx = result_obj.unwrap_err()

                    # Log with business context
                    self.logger.error(
                        f"❌ Analysis failed: {error_ctx.message}",
                        extra={
                            "category": error_ctx.category.value,
                            "phase": error_ctx.phase,
                            "technical_detail": error_ctx.technical_detail
                        }
                    )
                    log_analysis_complete(self.logger, duration, False)

                    # Return PipelineResult with user-friendly error for backwards compatibility
                    return PipelineResult(
                        success=False,
                        state=state,
                        error=error_ctx.user_message(),
                        execution_time=duration,
                        phase_times={}
                    )

            except Exception as e:
                # Catch-all for unexpected errors not handled by Result pattern
                duration = time.time() - start_time
                self.logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
                log_analysis_complete(self.logger, duration, False)

                return PipelineResult(
                    success=False,
                    state=state,
                    error="系统发生意外错误,请稍后重试",
                    execution_time=duration,
                    phase_times={}
                )

            finally:
                # Remove from active analyses
                if analysis_id in self._active_analyses:
                    del self._active_analyses[analysis_id]
                    self.logger.info("🔓 Released analysis slot")

    async def analyze_with_streaming(
        self,
        request: AnalysisRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run analysis with streaming progress updates.

        Args:
            request: Analysis request

        Yields:
            Progress updates as dictionaries
        """
        async with self._semaphore:
            self._runner.initialize_pipeline()

            async for update in self._runner.run_with_streaming(request):
                yield update

    def get_active_analyses(self) -> Dict[str, AnalysisState]:
        """Get currently active analyses."""
        return self._active_analyses.copy()

    def get_active_count(self) -> int:
        """Get count of active analyses."""
        return len(self._active_analyses)

    def get_available_slots(self) -> int:
        """Get number of available analysis slots."""
        return self.config.max_concurrent_analyses - len(self._active_analyses)

    def clear_cache(self) -> int:
        """
        Clear the result cache.

        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        return count

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return {
            "enabled": self.config.enable_caching,
            "entries": len(self._cache),
            "ttl_seconds": self.config.cache_ttl_seconds
        }


def create_analysis_service(
    settings: Optional[Settings] = None,
    config: Optional[AnalysisServiceConfig] = None
) -> AnalysisService:
    """
    Factory function to create an analysis service.

    Args:
        settings: Application settings
        config: Service configuration

    Returns:
        Configured AnalysisService
    """
    return AnalysisService(settings, config)


async def quick_analysis(
    category: str,
    target_market: str = "US",
    business_model: str = "amazon_fba",
    budget_range: str = "medium"
) -> PipelineResult:
    """
    Quick analysis helper for simple use cases.

    Args:
        category: Product category
        target_market: Target market
        business_model: Business model
        budget_range: Budget range

    Returns:
        Analysis result
    """
    request = AnalysisRequest(
        category=category,
        target_market=target_market,
        business_model=business_model,
        budget_range=budget_range
    )

    service = create_analysis_service()
    return await service.analyze(request)
