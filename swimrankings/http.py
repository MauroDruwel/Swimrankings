"""
Centralized HTTP client with Cloudflare bypass via browser TLS impersonation.
"""

from typing import Any

from curl_cffi import requests as cffi_requests

from .exceptions import NetworkError


_session: Any = None


def _get_session() -> cffi_requests.Session:
    global _session
    if _session is None:
        _session = cffi_requests.Session(impersonate="chrome120")
    return _session


def get(url: str, **kwargs: Any) -> cffi_requests.Response:
    """
    Perform a GET request with browser TLS impersonation to bypass Cloudflare.

    Do NOT pass custom ``headers=`` — curl_cffi sets browser-realistic headers
    automatically as part of the impersonation. Overriding them can break the
    bypass.

    Raises:
        NetworkError: On connection failure, Cloudflare challenge, or HTTP error.
    """
    try:
        response = _get_session().get(url, **kwargs)
    except cffi_requests.exceptions.RequestException as e:
        raise NetworkError(f"HTTP request failed: {e}") from e

    # Detect Cloudflare challenge / interstitial before raise_for_status
    if response.status_code in (403, 503):
        body = response.text[:2000].lower()
        if "just a moment" in body or "checking your browser" in body:
            raise NetworkError(
                "Cloudflare challenge page detected. Browser impersonation may "
                "not be working correctly for this request."
            )

    try:
        response.raise_for_status()
    except cffi_requests.exceptions.RequestException as e:
        raise NetworkError(f"HTTP {response.status_code} error: {e}") from e

    return response
