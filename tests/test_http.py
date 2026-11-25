"""
Tests for the centralized HTTP client module.
"""

import pytest
from unittest.mock import Mock, patch

from swimrankings.exceptions import AuthenticationError, NetworkError
import swimrankings.http as http_module


@pytest.fixture(autouse=True)
def reset_state(tmp_path, monkeypatch):
    """Reset module-level state and isolate the on-disk cache per test."""
    monkeypatch.setenv("SWIMRANKINGS_CACHE_DIR", str(tmp_path))
    original_session = http_module._session
    original_last = http_module._last_refresh
    original_auth = http_module._auth
    http_module._session = None
    http_module._last_refresh = 0.0
    http_module._auth = None
    yield
    http_module._session = original_session
    http_module._last_refresh = original_last
    http_module._auth = original_auth


def _make_response(status_code=200, text="<html>OK</html>", url="https://example.com"):
    resp = Mock()
    resp.status_code = status_code
    resp.text = text
    resp.url = url
    resp.raise_for_status.return_value = None
    return resp


CF_BODY = "<html><title>Just a moment...</title><body>just a moment</body></html>"


class TestHttpGet:
    """Tests for swimrankings.http.get()."""

    @patch("swimrankings.http.cffi_requests.Session")
    def test_successful_get(self, MockSession):
        """Successful request returns the response object."""
        resp = _make_response()
        MockSession.return_value.get.return_value = resp

        result = http_module.get("https://example.com", params={"foo": "bar"})

        assert result is resp
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

        resp = _make_response(status_code=404)
        resp.raise_for_status.side_effect = RequestException("404 Not Found")
        MockSession.return_value.get.return_value = resp

        with pytest.raises(NetworkError) as exc_info:
            http_module.get("https://example.com")

        assert "HTTP 404" in str(exc_info.value)

    @patch("swimrankings.http._solve_challenge_with_browser")
    @patch("swimrankings.http.cffi_requests.Session")
    def test_cloudflare_challenge_is_solved_and_retried(self, MockSession, mock_solve):
        """A Cloudflare challenge triggers a browser solve and a retried request."""
        cf_resp = _make_response(
            status_code=403, text=CF_BODY, url="https://example.com/index.php?x=1"
        )
        ok_resp = _make_response()
        MockSession.return_value.get.side_effect = [cf_resp, ok_resp]
        mock_solve.return_value = {
            "cookies": {"cf_clearance": "abc"},
            "user_agent": "UA",
            "ts": 0,
        }

        result = http_module.get("https://example.com/index.php", params={"x": 1})

        assert result is ok_resp
        # The browser is pointed at the exact challenged URL (including params).
        mock_solve.assert_called_once()
        assert mock_solve.call_args[0][0] == "https://example.com/index.php?x=1"
        assert MockSession.return_value.get.call_count == 2

    @patch("swimrankings.http._solve_challenge_with_browser")
    @patch("swimrankings.http.cffi_requests.Session")
    def test_cloudflare_challenge_persisting_raises(self, MockSession, mock_solve):
        """If the challenge is still present after solving, NetworkError is raised."""
        cf_resp = _make_response(status_code=403, text=CF_BODY)
        MockSession.return_value.get.return_value = cf_resp
        mock_solve.return_value = {
            "cookies": {"cf_clearance": "abc"},
            "user_agent": "UA",
            "ts": 0,
        }

        with pytest.raises(NetworkError) as exc_info:
            http_module.get("https://example.com/index.php")

        assert "Cloudflare" in str(exc_info.value)

    @patch("swimrankings.http.cffi_requests.Session")
    def test_normal_403_not_cf_still_raises(self, MockSession):
        """A normal 403 without CF body keywords still raises via raise_for_status."""
        from curl_cffi.requests.exceptions import RequestException

        resp = _make_response(status_code=403, text="<html>Forbidden</html>")
        resp.raise_for_status.side_effect = RequestException("403 Forbidden")
        MockSession.return_value.get.return_value = resp

        with pytest.raises(NetworkError):
            http_module.get("https://example.com")

    @patch("swimrankings.http.cffi_requests.Session")
    def test_session_is_reused(self, MockSession):
        """The Session is created once and reused across calls."""
        MockSession.return_value.get.return_value = _make_response()

        http_module.get("https://example.com/1")
        http_module.get("https://example.com/2")

        MockSession.assert_called_once()

    @patch("swimrankings.http.cffi_requests.Session")
    def test_session_created_with_impersonation(self, MockSession):
        """Session is created with a chrome impersonation target."""
        MockSession.return_value.get.return_value = _make_response()

        http_module.get("https://example.com")

        call_kwargs = MockSession.call_args[1]
        assert "chrome" in call_kwargs.get("impersonate", "").lower()


class TestClearanceCache:
    """Tests for the on-disk clearance cache and its application to a session."""

    def test_save_and_load_roundtrip(self):
        state = {
            "cookies": {"cf_clearance": "tok", "PHPSESSID": "sid"},
            "user_agent": "UA",
            "ts": http_module.time.time(),
        }
        http_module._save_state(state)

        loaded = http_module._load_state()
        assert loaded is not None
        assert loaded["cookies"]["cf_clearance"] == "tok"
        assert loaded["user_agent"] == "UA"

    def test_expired_cache_is_ignored(self):
        state = {
            "cookies": {"cf_clearance": "tok"},
            "user_agent": "UA",
            "ts": http_module.time.time() - http_module.CACHE_MAX_AGE - 10,
        }
        http_module._save_state(state)

        assert http_module._load_state() is None

    def test_cache_without_clearance_is_ignored(self):
        http_module._save_state(
            {"cookies": {"PHPSESSID": "sid"}, "user_agent": "UA", "ts": 0}
        )
        assert http_module._load_state() is None

    def test_apply_state_sets_user_agent_and_cookies(self):
        session = Mock()
        session.headers = {}
        session.cookies = Mock()

        http_module._apply_state(
            session,
            {"cookies": {"cf_clearance": "tok"}, "user_agent": "UA"},
        )

        assert session.headers["User-Agent"] == "UA"
        session.cookies.set.assert_called_once_with(
            "cf_clearance", "tok", domain=http_module.COOKIE_DOMAIN
        )

    @patch("swimrankings.http.cffi_requests.Session")
    def test_cached_clearance_applied_on_session_create(self, MockSession):
        """A cached clearance is loaded onto a freshly created session."""
        MockSession.return_value.headers = {}
        MockSession.return_value.cookies = Mock()
        http_module._save_state(
            {
                "cookies": {"cf_clearance": "tok"},
                "user_agent": "UA",
                "ts": http_module.time.time(),
            }
        )

        http_module._get_session()

        assert MockSession.return_value.headers["User-Agent"] == "UA"
        MockSession.return_value.cookies.set.assert_called_once_with(
            "cf_clearance", "tok", domain=http_module.COOKIE_DOMAIN
        )


class TestHttpAuthentication:
    """Tests for Swimrankings Member authentication and session handling."""

    @patch("swimrankings.http.cffi_requests.Session")
    def test_http_401_raises_authentication_error(self, MockSession):
        """HTTP 401 raises an AuthenticationError with helpful guidance."""
        resp = _make_response(status_code=401, text="Unauthorized")
        MockSession.return_value.get.return_value = resp

        with pytest.raises(AuthenticationError) as exc_info:
            http_module.get("https://example.com/index.php?page=athleteDetail")

        assert "Swimrankings Member account" in str(exc_info.value)
        assert isinstance(exc_info.value, NetworkError)

    def test_set_auth_and_get_auth(self):
        """set_auth stores credentials in module state and on active session."""
        mock_session = Mock()
        http_module._session = mock_session

        http_module.set_auth("swimmer@example.com", "secret123")

        assert http_module.get_auth() == ("swimmer@example.com", "secret123")
        assert mock_session.auth == ("swimmer@example.com", "secret123")

        http_module.set_auth(None, None)
        assert http_module.get_auth() is None
        assert mock_session.auth is None

    def test_get_auth_from_environment_username(self, monkeypatch):
        """SWIMRANKINGS_USERNAME and SWIMRANKINGS_PASSWORD are used."""
        monkeypatch.setenv("SWIMRANKINGS_USERNAME", "env_user@example.com")
        monkeypatch.setenv("SWIMRANKINGS_PASSWORD", "env_pass")

        assert http_module.get_auth() == ("env_user@example.com", "env_pass")

    def test_get_auth_from_environment_email(self, monkeypatch):
        """SWIMRANKINGS_EMAIL is supported as a fallback for username."""
        monkeypatch.setenv("SWIMRANKINGS_EMAIL", "email_user@example.com")
        monkeypatch.setenv("SWIMRANKINGS_PASSWORD", "env_pass")

        assert http_module.get_auth() == ("email_user@example.com", "env_pass")

    @patch("swimrankings.http.cffi_requests.Session")
    def test_session_init_with_auth(self, MockSession):
        """A new session adopts effective auth if configured."""
        http_module.set_auth("user@test.com", "pw")
        http_module._get_session()

        assert MockSession.return_value.auth == ("user@test.com", "pw")

    @patch("swimrankings.http.cffi_requests.Session")
    def test_get_uses_effective_auth(self, MockSession):
        """http.get() passes configured auth when no explicit auth is given."""
        http_module.set_auth("user@test.com", "pw")
        MockSession.return_value.get.return_value = _make_response()

        http_module.get("https://example.com")

        MockSession.return_value.get.assert_called_once_with(
            "https://example.com", auth=("user@test.com", "pw")
        )

    @patch("swimrankings.http.cffi_requests.Session")
    def test_get_uses_explicit_auth_argument(self, MockSession):
        """Explicit auth kwarg overrides configured credentials."""
        http_module.set_auth("configured@test.com", "pw1")
        MockSession.return_value.get.return_value = _make_response()

        http_module.get("https://example.com", auth=("explicit@test.com", "pw2"))

        MockSession.return_value.get.assert_called_once_with(
            "https://example.com", auth=("explicit@test.com", "pw2")
        )

    @patch("swimrankings.http.cffi_requests.Session")
    def test_login_success(self, MockSession):
        """login() submits credentials and stores auth on success."""
        ok_resp = _make_response(status_code=200, text="<html>Dashboard</html>")
        MockSession.return_value.post.return_value = ok_resp

        result = http_module.login("user@test.com", "correct_pass")

        assert result is True
        assert http_module.get_auth() == ("user@test.com", "correct_pass")
        MockSession.return_value.post.assert_called_once()
        args, kwargs = MockSession.return_value.post.call_args
        assert kwargs["data"]["lemail"] == "user@test.com"
        assert kwargs["data"]["lpassword"] == "correct_pass"

    @patch("swimrankings.http.cffi_requests.Session")
    def test_login_failure(self, MockSession):
        """login() raises AuthenticationError when credentials are invalid."""
        err_resp = _make_response(
            status_code=200, text="<html>Email or password is incorrect</html>"
        )
        MockSession.return_value.post.return_value = err_resp

        with pytest.raises(AuthenticationError) as exc_info:
            http_module.login("user@test.com", "wrong_pass")

        assert "Email or password is incorrect" in str(exc_info.value)
        assert http_module.get_auth() is None

    @patch("swimrankings.http.cffi_requests.Session")
    def test_http_401_with_credentials_raises_rejected_error(self, MockSession):
        """HTTP 401 when auth was supplied reports invalid credentials."""
        resp = _make_response(status_code=401, text="Unauthorized")
        MockSession.return_value.get.return_value = resp

        with pytest.raises(AuthenticationError) as exc_info:
            http_module.get(
                "https://example.com/index.php?page=athleteDetail",
                auth=("bad@test.com", "wrong"),
            )

        assert "rejected the provided credentials" in str(exc_info.value)

    @patch("swimrankings.http.cffi_requests.Session")
    def test_login_failure_localized_error_span(self, MockSession):
        """login() detects error span inside #loginForm regardless of language."""
        err_resp = _make_response(
            status_code=200,
            text='<form id="loginForm"><span class="error">Ongeldig</span></form>',
        )
        MockSession.return_value.post.return_value = err_resp

        with pytest.raises(AuthenticationError):
            http_module.login("user@test.com", "wrong_pass")

        assert http_module.get_auth() is None

    @patch("swimrankings.http._solve_challenge_with_browser")
    @patch("swimrankings.http.cffi_requests.Session")
    def test_login_solves_cloudflare_challenge(self, MockSession, mock_solve):
        """login() transparently solves Cloudflare challenge before retrying POST."""
        cf_resp = _make_response(
            status_code=403, text=CF_BODY, url="https://www.swimrankings.net/index.php"
        )
        ok_resp = _make_response(status_code=200, text="<html>Logged in</html>")
        MockSession.return_value.post.side_effect = [cf_resp, ok_resp]
        mock_solve.return_value = {
            "cookies": {"cf_clearance": "abc"},
            "user_agent": "UA",
            "ts": 0,
        }

        result = http_module.login("user@test.com", "correct_pass")

        assert result is True
        mock_solve.assert_called_once()
        assert MockSession.return_value.post.call_count == 2
        assert http_module.get_auth() == ("user@test.com", "correct_pass")

    @patch("swimrankings.http.cffi_requests.Session")
    def test_login_http_error_raises_network_error(self, MockSession):
        """login() raises NetworkError on HTTP 5xx response."""
        from curl_cffi.requests.exceptions import RequestException

        err_resp = _make_response(status_code=500, text="Server Error")
        err_resp.raise_for_status.side_effect = RequestException("500 Server Error")
        MockSession.return_value.post.return_value = err_resp

        with pytest.raises(NetworkError) as exc_info:
            http_module.login("user@test.com", "pass")

        assert "HTTP 500" in str(exc_info.value)
        assert http_module.get_auth() is None

    @patch("swimrankings.http.cffi_requests.Session")
    def test_login_network_error(self, MockSession):
        """login() raises NetworkError when request fails."""
        from curl_cffi.requests.exceptions import RequestException

        MockSession.return_value.post.side_effect = RequestException("Timeout")

        with pytest.raises(NetworkError) as exc_info:
            http_module.login("user@test.com", "pass")

        assert "HTTP request failed" in str(exc_info.value)
