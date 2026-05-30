"""
Tests for the centralized HTTP client module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from swimrankings.exceptions import NetworkError
import swimrankings.http as http_module


@pytest.fixture(autouse=True)
def reset_session():
    """Reset the module-level session before each test."""
    original = http_module._session
    http_module._session = None
    yield
    http_module._session = original


class TestHttpGet:
    """Tests for swimrankings.http.get()."""

    def _make_response(self, status_code=200, text="<html>OK</html>", headers=None):
        mock_resp = Mock()
        mock_resp.status_code = status_code
        mock_resp.text = text
        mock_resp.headers = headers or {}
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    @patch("swimrankings.http.cffi_requests.Session")
    def test_successful_get(self, MockSession):
        """Successful request returns the response object."""
        mock_resp = self._make_response()
        MockSession.return_value.get.return_value = mock_resp

        result = http_module.get("https://example.com", params={"foo": "bar"})

        assert result is mock_resp
        MockSession.return_value.get.assert_called_once_with(
            "https://example.com", params={"foo": "bar"}
        )

    @patch("swimrankings.http.cffi_requests.Session")
    def test_connection_error_raises_network_error(self, MockSession):
        """Connection-level errors from curl_cffi become NetworkError."""
        from curl_cffi.requests.exceptions import RequestException

        MockSession.return_value.get.side_effect = RequestException("timeout")

        with pytest.raises(NetworkError) as exc_info:
            http_module.get("https://example.com")

        assert "HTTP request failed" in str(exc_info.value)

    @patch("swimrankings.http.cffi_requests.Session")
    def test_http_error_raises_network_error(self, MockSession):
        """HTTP 4xx/5xx errors become NetworkError after raise_for_status."""
        from curl_cffi.requests.exceptions import RequestException

        mock_resp = self._make_response(status_code=404)
        mock_resp.raise_for_status.side_effect = RequestException("404 Not Found")
        MockSession.return_value.get.return_value = mock_resp

        with pytest.raises(NetworkError) as exc_info:
            http_module.get("https://example.com")

        assert "HTTP 404" in str(exc_info.value)

    @patch("swimrankings.http.cffi_requests.Session")
    def test_cloudflare_challenge_403_raises_network_error(self, MockSession):
        """A 403 with 'just a moment' body is detected as a Cloudflare challenge."""
        cf_body = "<html><title>Just a moment...</title><body>just a moment</body></html>"
        mock_resp = self._make_response(status_code=403, text=cf_body)
        MockSession.return_value.get.return_value = mock_resp

        with pytest.raises(NetworkError) as exc_info:
            http_module.get("https://example.com")

        assert "Cloudflare" in str(exc_info.value)

    @patch("swimrankings.http.cffi_requests.Session")
    def test_cloudflare_challenge_503_checking_browser(self, MockSession):
        """A 503 with 'checking your browser' body is a Cloudflare challenge."""
        cf_body = "<html><body>Checking your browser before accessing the site.</body></html>"
        mock_resp = self._make_response(status_code=503, text=cf_body)
        MockSession.return_value.get.return_value = mock_resp

        with pytest.raises(NetworkError) as exc_info:
            http_module.get("https://example.com")

        assert "Cloudflare" in str(exc_info.value)

    @patch("swimrankings.http.cffi_requests.Session")
    def test_normal_403_not_cf_still_raises(self, MockSession):
        """A normal 403 without CF body keywords still raises via raise_for_status."""
        from curl_cffi.requests.exceptions import RequestException

        mock_resp = self._make_response(status_code=403, text="<html>Forbidden</html>")
        mock_resp.raise_for_status.side_effect = RequestException("403 Forbidden")
        MockSession.return_value.get.return_value = mock_resp

        with pytest.raises(NetworkError):
            http_module.get("https://example.com")

    @patch("swimrankings.http.cffi_requests.Session")
    def test_session_is_reused(self, MockSession):
        """The Session is created once and reused across calls."""
        mock_resp = self._make_response()
        MockSession.return_value.get.return_value = mock_resp

        http_module.get("https://example.com/1")
        http_module.get("https://example.com/2")

        MockSession.assert_called_once()

    @patch("swimrankings.http.cffi_requests.Session")
    def test_session_created_with_impersonation(self, MockSession):
        """Session is created with a chrome impersonation target."""
        mock_resp = self._make_response()
        MockSession.return_value.get.return_value = mock_resp

        http_module.get("https://example.com")

        call_kwargs = MockSession.call_args[1]
        assert "chrome" in call_kwargs.get("impersonate", "").lower()
