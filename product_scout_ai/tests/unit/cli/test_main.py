"""
Tests for cli/main.py
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import tempfile
import os

from src.cli.main import (
    create_parser,
    parse_args,
    run_analysis,
    main,
)
from src.schemas.state_schemas import AnalysisState
from src.workflows.analysis_pipeline import PipelineResult
from src.services import analysis_service as analysis_svc


class TestCreateParser:
    """Test cases for create_parser function."""

    def test_creates_parser(self):
        """Test parser is created."""
        parser = create_parser()

        assert parser is not None
        assert parser.prog == "product_scout"

    def test_parser_has_analyze_command(self):
        """Test parser has analyze subcommand."""
        parser = create_parser()
        args = parser.parse_args(["analyze", "test category"])

        assert args.command == "analyze"
        assert args.category == "test category"

    def test_parser_version(self):
        """Test parser has version argument."""
        parser = create_parser()

        # Version flag causes SystemExit
        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])


class TestParseArgs:
    """Test cases for parse_args function."""

    def test_analyze_command_basic(self):
        """Test parsing basic analyze command."""
        args = parse_args(["analyze", "portable blender"])

        assert args.command == "analyze"
        assert args.category == "portable blender"
        assert args.market == "US"  # default
        assert args.budget == "medium"  # default
        assert args.model == "amazon_fba"  # default
        assert args.output == "markdown"  # default

    def test_analyze_with_market(self):
        """Test parsing analyze with market option."""
        args = parse_args(["analyze", "blender", "--market", "EU"])

        assert args.market == "EU"

    def test_analyze_with_short_market(self):
        """Test parsing analyze with short market option."""
        args = parse_args(["analyze", "blender", "-m", "UK"])

        assert args.market == "UK"

    def test_analyze_with_budget(self):
        """Test parsing analyze with budget option."""
        args = parse_args(["analyze", "blender", "--budget", "high"])

        assert args.budget == "high"

    def test_analyze_with_short_budget(self):
        """Test parsing analyze with short budget option."""
        args = parse_args(["analyze", "blender", "-b", "low"])

        assert args.budget == "low"

    def test_analyze_with_model(self):
        """Test parsing analyze with model option."""
        args = parse_args(["analyze", "blender", "--model", "dropshipping"])

        assert args.model == "dropshipping"

    def test_analyze_with_output(self):
        """Test parsing analyze with output option."""
        args = parse_args(["analyze", "blender", "--output", "json"])

        assert args.output == "json"

    def test_analyze_with_file(self):
        """Test parsing analyze with file option."""
        args = parse_args(["analyze", "blender", "--file", "output.json"])

        assert args.file == "output.json"

    def test_analyze_with_verbose(self):
        """Test parsing analyze with verbose flag."""
        args = parse_args(["analyze", "blender", "--verbose"])

        assert args.verbose is True

    def test_analyze_with_short_verbose(self):
        """Test parsing analyze with short verbose flag."""
        args = parse_args(["analyze", "blender", "-v"])

        assert args.verbose is True

    def test_analyze_all_options(self):
        """Test parsing analyze with all options."""
        args = parse_args([
            "analyze", "smart watch",
            "-m", "EU",
            "-b", "high",
            "-M", "private_label",
            "-o", "json",
            "-f", "report.json",
            "-v"
        ])

        assert args.category == "smart watch"
        assert args.market == "EU"
        assert args.budget == "high"
        assert args.model == "private_label"
        assert args.output == "json"
        assert args.file == "report.json"
        assert args.verbose is True

    def test_no_command(self):
        """Test parsing with no command."""
        args = parse_args([])

        assert args.command is None

    def test_invalid_market_rejected(self):
        """Test invalid market is rejected."""
        with pytest.raises(SystemExit):
            parse_args(["analyze", "blender", "--market", "INVALID"])

    def test_invalid_budget_rejected(self):
        """Test invalid budget is rejected."""
        with pytest.raises(SystemExit):
            parse_args(["analyze", "blender", "--budget", "invalid"])


class TestRunAnalysis:
    """Test cases for run_analysis function."""

    @pytest.fixture
    def basic_args(self):
        """Create basic args."""
        return parse_args(["analyze", "portable blender"])

    @pytest.fixture
    def verbose_args(self):
        """Create verbose args."""
        return parse_args(["analyze", "blender", "-v"])

    @pytest.fixture
    def mock_result(self):
        """Create mock pipeline result."""
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
            error="API error",
            execution_time=1.0
        )

    @pytest.mark.asyncio
    async def test_run_analysis_success(self, basic_args, mock_result, capsys):
        """Test successful analysis run."""
        with patch.object(analysis_svc, 'create_analysis_service') as mock_create_service:
            mock_service = Mock()
            mock_service.analyze = AsyncMock(return_value=mock_result)
            mock_create_service.return_value = mock_service

            exit_code = await run_analysis(basic_args)

            assert exit_code == 0
            mock_service.analyze.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_analysis_failure(self, basic_args, failed_result, capsys):
        """Test failed analysis run."""
        with patch.object(analysis_svc, 'create_analysis_service') as mock_create_service:
            mock_service = Mock()
            mock_service.analyze = AsyncMock(return_value=failed_result)
            mock_create_service.return_value = mock_service

            exit_code = await run_analysis(basic_args)

            assert exit_code == 1
            captured = capsys.readouterr()
            assert "API error" in captured.err

    @pytest.mark.asyncio
    async def test_run_analysis_verbose(self, verbose_args, mock_result, capsys):
        """Test verbose analysis run."""
        with patch.object(analysis_svc, 'create_analysis_service') as mock_create_service:
            mock_service = Mock()
            mock_service.analyze = AsyncMock(return_value=mock_result)
            mock_create_service.return_value = mock_service

            exit_code = await run_analysis(verbose_args)

            assert exit_code == 0
            captured = capsys.readouterr()
            assert "Analyzing" in captured.out

    @pytest.mark.asyncio
    async def test_run_analysis_json_output(self, mock_result, capsys):
        """Test JSON output format."""
        with patch.object(analysis_svc, 'create_analysis_service') as mock_create_service:
            args = parse_args(["analyze", "blender", "-o", "json"])
            mock_service = Mock()
            mock_service.analyze = AsyncMock(return_value=mock_result)
            mock_create_service.return_value = mock_service

            exit_code = await run_analysis(args)

            assert exit_code == 0
            captured = capsys.readouterr()
            assert "{" in captured.out  # JSON output

    @pytest.mark.asyncio
    async def test_run_analysis_markdown_output(self, mock_result, capsys):
        """Test Markdown output format."""
        with patch.object(analysis_svc, 'create_analysis_service') as mock_create_service:
            args = parse_args(["analyze", "blender", "-o", "markdown"])
            mock_service = Mock()
            mock_service.analyze = AsyncMock(return_value=mock_result)
            mock_create_service.return_value = mock_service

            exit_code = await run_analysis(args)

            assert exit_code == 0
            captured = capsys.readouterr()
            assert "#" in captured.out  # Markdown heading

    @pytest.mark.asyncio
    async def test_run_analysis_file_output(self, mock_result):
        """Test file output."""
        with patch.object(analysis_svc, 'create_analysis_service') as mock_create_service:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                temp_path = f.name

            try:
                args = parse_args(["analyze", "blender", "-o", "json", "-f", temp_path])
                mock_service = Mock()
                mock_service.analyze = AsyncMock(return_value=mock_result)
                mock_create_service.return_value = mock_service

                exit_code = await run_analysis(args)

                assert exit_code == 0
                assert os.path.exists(temp_path)
                with open(temp_path, 'r') as f:
                    content = f.read()
                    assert "{" in content
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_run_analysis_exception(self, basic_args, capsys):
        """Test exception handling."""
        with patch.object(analysis_svc, 'create_analysis_service') as mock_create_service:
            mock_service = Mock()
            mock_service.analyze = AsyncMock(side_effect=Exception("Network error"))
            mock_create_service.return_value = mock_service

            exit_code = await run_analysis(basic_args)

            assert exit_code == 1
            captured = capsys.readouterr()
            assert "Network error" in captured.err


class TestMain:
    """Test cases for main function."""

    def test_main_no_command(self, capsys):
        """Test main with no command."""
        exit_code = main([])

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "ProductScout" in captured.out

    def test_main_analyze_command(self):
        """Test main with analyze command."""
        with patch('asyncio.run') as mock_asyncio_run:
            mock_asyncio_run.return_value = 0

            exit_code = main(["analyze", "blender"])

            mock_asyncio_run.assert_called_once()
            assert exit_code == 0

    def test_main_uses_sys_argv(self, monkeypatch):
        """Test main uses sys.argv when no args provided."""
        monkeypatch.setattr(sys, 'argv', ['product_scout'])

        exit_code = main()

        # No command, should print help and return 0
        assert exit_code == 0


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_help_text(self, capsys):
        """Test help text is displayed."""
        parser = create_parser()
        parser.print_help()

        captured = capsys.readouterr()
        assert "ProductScout" in captured.out
        assert "analyze" in captured.out

    def test_analyze_help_text(self, capsys):
        """Test analyze help text."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["analyze", "--help"])

        captured = capsys.readouterr()
        assert "category" in captured.out
        assert "--market" in captured.out
