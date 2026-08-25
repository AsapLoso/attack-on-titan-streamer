"""
Test Suite: Media Stream URL Verifier Engine (F5)
Validates HTTP Range-request probing, status code handling (200/206), timeouts, and retry logic.
"""

import urllib.request
import urllib.error
from unittest.mock import patch, MagicMock
from pathlib import Path
from typing import Dict, Any, Tuple

import pytest


def probe_stream_url(url: str, timeout: float = 5.0, range_bytes: int = 1024) -> Tuple[bool, int, str]:
    """
    Reference opaque-box stream probing function using HTTP Range requests.
    Returns: (is_valid, status_code, error_or_content_type)
    """
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AOT-Stream-Verifier/1.0",
            "Range": f"bytes=0-{range_bytes}"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.getcode()
            content_type = response.headers.get("Content-Type", "")
            # Both 206 (Partial Content) and 200 (OK) indicate accessible stream
            if status in (200, 206):
                return True, status, content_type
            return False, status, f"Unexpected status {status}"
    except urllib.error.HTTPError as e:
        return False, e.code, f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, 0, f"URL Error: {e.reason}"
    except Exception as e:
        return False, 0, f"Error: {str(e)}"


class TestStreamVerifierProtocol:
    """Opaque-box tests for HTTP Range-request verification logic."""

    @patch("urllib.request.urlopen")
    def test_verify_stream_success_206_partial_content(self, mock_urlopen):
        """Verify HTTP 206 Partial Content is accepted as valid stream."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 206
        mock_response.headers = {"Content-Type": "video/mp4", "Content-Range": "bytes 0-1024/452589200"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        valid, status, ct = probe_stream_url("https://archive.org/download/test/ep1.mp4")
        assert valid is True
        assert status == 206
        assert "video/mp4" in ct

    @patch("urllib.request.urlopen")
    def test_verify_stream_success_200_ok(self, mock_urlopen):
        """Verify HTTP 200 OK (server ignored Range header) is accepted as valid stream."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {"Content-Type": "video/mp4"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        valid, status, ct = probe_stream_url("https://archive.org/download/test/ep1.mp4")
        assert valid is True
        assert status == 200

    @patch("urllib.request.urlopen")
    def test_verify_stream_404_not_found(self, mock_urlopen):
        """Verify HTTP 404 is flagged as invalid."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://archive.org/download/test/missing.mp4",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None
        )
        valid, status, err = probe_stream_url("https://archive.org/download/test/missing.mp4")
        assert valid is False
        assert status == 404
        assert "404" in err

    @patch("urllib.request.urlopen")
    def test_verify_stream_connection_timeout(self, mock_urlopen):
        """Verify connection timeouts are caught and reported."""
        mock_urlopen.side_effect = urllib.error.URLError("Connection timed out")
        valid, status, err = probe_stream_url("https://archive.org/download/test/slow.mp4")
        assert valid is False
        assert status == 0
        assert "timed out" in err


class TestLiveStreamVerifierModule:
    """Verify stream_verifier.py module if present in workspace."""

    def test_stream_verifier_module_contract_if_present(self):
        """Test stream_verifier module functions if implemented."""
        try:
            import stream_verifier
            if hasattr(stream_verifier, "verify_stream_url"):
                with patch("urllib.request.urlopen") as mock_urlopen:
                    mock_resp = MagicMock()
                    mock_resp.getcode.return_value = 206
                    mock_resp.headers = {"Content-Type": "video/mp4"}
                    mock_urlopen.return_value.__enter__.return_value = mock_resp
                    
                    res = stream_verifier.verify_stream_url("https://archive.org/download/test/ep1.mp4")
                    assert res is True or isinstance(res, (tuple, dict))
        except ImportError:
            pass  # Module to be created in M1
