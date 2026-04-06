"""Tests for wolfravant_mcp.server."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from wolfravant_mcp.server import _format_result, wolfram_alpha


def _make_pod(title: str, plaintext: str) -> dict:
    return {"@title": title, "subpod": [{"plaintext": plaintext}]}


def _make_result(success: bool, pods: list[dict] | None = None) -> MagicMock:
    res = MagicMock()
    res.success = success
    res.pods = pods or []
    return res


class TestFormatResult:
    def test_success_with_pods(self):
        res = _make_result(True, [_make_pod("Input", "x^2"), _make_pod("Result", "2x")])
        out = _format_result(res)
        assert "## Input" in out
        assert "x^2" in out
        assert "## Result" in out
        assert "2x" in out

    def test_failure_no_suggestions(self):
        res = _make_result(False)
        res.didyoumeans = None
        out = _format_result(res)
        assert "No results" in out

    def test_failure_with_suggestions(self):
        res = _make_result(False)
        res.didyoumeans = [{"#text": "integrate"}]
        out = _format_result(res)
        assert "Did you mean" in out
        assert "integrate" in out

    def test_success_no_text(self):
        res = _make_result(True, [{"@title": "Plot", "subpod": [{"plaintext": None}]}])
        out = _format_result(res)
        assert "no displayable text" in out


class TestWolframAlpha:
    @patch("wolfravant_mcp.server._get_client")
    def test_query_calls_client(self, mock_get_client):
        mock_client = MagicMock()
        mock_result = _make_result(True, [_make_pod("Result", "42")])
        mock_client.query.return_value = mock_result
        mock_get_client.return_value = mock_client

        out = wolfram_alpha("answer to everything")
        mock_client.query.assert_called_once_with("answer to everything")
        assert "42" in out

    @patch("wolfravant_mcp.server._get_client")
    def test_api_error_handled(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.side_effect = ConnectionError("timeout")
        mock_get_client.return_value = mock_client

        out = wolfram_alpha("fail query")
        assert "API error" in out
        assert "timeout" in out
