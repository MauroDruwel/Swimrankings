"""
Centralized HTTP client with Cloudflare bypass.

swimrankings.net protects its ``/index.php`` endpoints with Cloudflare's
"Just a moment..." managed JavaScript challenge. Plain HTTP clients -- even
with TLS impersonation -- cannot pass it because it requires executing the
challenge JavaScript in a real browser.

Strategy used here:

1. All requests go through a long-lived ``curl_cffi`` session that impersonates
   a real Chrome TLS fingerprint. This is fast and handles the bulk of traffic.
2. The first time a request hits a Cloudflare challenge, a real Chrome browser
   (driven by ``nodriver``) solves it once and yields a ``cf_clearance`` cookie
   plus the matching ``User-Agent``.
3. That clearance is injected into the ``curl_cffi`` session and persisted to a
   small on-disk cache, so subsequent requests -- and subsequent process runs --
   stay on the fast path until the clearance expires.
4. When the clearance expires, the next challenged request transparently
   re-solves via the browser.

No third-party services, accounts, or API keys are involved; everything runs
locally against a Chrome/Chromium install.
"""

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

from curl_cffi import requests as cffi_requests

from .exceptions import NetworkError


# TLS fingerprint to impersonate. A recent Chrome keeps us consistent with the
# User-Agent reported by the browser that solves the challenge.
IMPERSONATE = "chrome"

# Cookie domain used by swimrankings.net.
COOKIE_DOMAIN = ".swimrankings.net"

# How long to let the browser work on a single challenge before giving up.
BROWSER_TIMEOUT = 45

# Ignore cached clearance older than this (seconds); cf_clearance is short-lived.
CACHE_MAX_AGE = 2 * 60 * 60

# Cool-down window during which concurrent callers reuse a fresh clearance
# instead of each launching their own browser.
REFRESH_COOLDOWN = 30


_session: Optional[Any] = None
_session_lock = threading.Lock()
_refresh_lock = threading.Lock()
_last_refresh = 0.0
_display: Any = None


# --------------------------------------------------------------------------- #
# On-disk clearance cache
# --------------------------------------------------------------------------- #
def _cache_file() -> Path:
    base = os.environ.get("SWIMRANKINGS_CACHE_DIR")
    directory = Path(base) if base else Path.home() / ".cache" / "swimrankings"
    return directory / "cf_state.json"


def _load_state() -> Optional[Dict[str, Any]]:
    path = _cache_file()
    try:
        with path.open("r", encoding="utf-8") as handle:
            state = json.load(handle)
    except (OSError, ValueError):
        return None

    if not isinstance(state, dict) or "cf_clearance" not in state.get("cookies", {}):
        return None
    if time.time() - float(state.get("ts", 0)) > CACHE_MAX_AGE:
        return None
    return state


def _save_state(state: Dict[str, Any]) -> None:
    path = _cache_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle)
        os.replace(tmp, path)
    except OSError:
        # A failed cache write is non-fatal; we simply re-solve next time.
        pass


# --------------------------------------------------------------------------- #
# Session management
# --------------------------------------------------------------------------- #
def _apply_state(session: Any, state: Dict[str, Any]) -> None:
    user_agent = state.get("user_agent")
    if user_agent:
        session.headers["User-Agent"] = user_agent
    for name, value in state.get("cookies", {}).items():
        session.cookies.set(name, value, domain=COOKIE_DOMAIN)


def _get_session() -> Any:
    global _session
    with _session_lock:
        if _session is None:
            _session = cffi_requests.Session(impersonate=IMPERSONATE)  # type: ignore[arg-type]
            state = _load_state()
            if state:
                _apply_state(_session, state)
        return _session


# --------------------------------------------------------------------------- #
# Cloudflare challenge detection
# --------------------------------------------------------------------------- #
def _is_cf_challenge(response: Any) -> bool:
    if response.status_code not in (403, 503):
        return False
    body = response.text[:3000].lower()
    return (
        "just a moment" in body
        or "checking your browser" in body
        or "cf-challenge" in body
        or "cf_chl_opt" in body
    )


# --------------------------------------------------------------------------- #
# Browser-based challenge solving
# --------------------------------------------------------------------------- #
def _maybe_start_display() -> None:
    """Start a virtual framebuffer when no display is available (headless box).

    Cloudflare detects headless Chrome, so the browser must run in headed mode;
    on a server with no X display we provide one via Xvfb.
    """
    global _display
    if os.environ.get("DISPLAY"):
        return
    if _display is not None:
        return
    try:
        from pyvirtualdisplay import Display
    except ImportError as exc:
        raise NetworkError(
            "Solving the Cloudflare challenge needs a display. No DISPLAY is set "
            "and 'pyvirtualdisplay' is not installed. Install it (and the system "
            "'xvfb' package), or run with an X server available."
        ) from exc

    _display = Display(visible=False, size=(1440, 900))
    _display.start()


def _browser_solve(url: str, timeout: int) -> Dict[str, Any]:
    import asyncio

    try:
        import nodriver as uc  # type: ignore[import-untyped]
    except ImportError as exc:
        raise NetworkError(
            "Solving the Cloudflare challenge requires the 'nodriver' package "
            "and a Chrome/Chromium install. Install nodriver to continue."
        ) from exc

    _maybe_start_display()

    browser_path = os.environ.get("SWIMRANKINGS_BROWSER_PATH")
    start_kwargs: Dict[str, Any] = {
        "headless": False,
        "browser_args": ["--no-sandbox", "--disable-gpu", "--window-size=1440,900"],
    }
    if browser_path:
        start_kwargs["browser_executable_path"] = browser_path

    async def _run() -> Optional[Dict[str, Any]]:
        browser = await uc.start(**start_kwargs)
        try:
            page = await browser.get(url)
            deadline = time.time() + timeout
            while time.time() < deadline:
                await asyncio.sleep(2)
                html = await page.get_content()
                if "just a moment" in html.lower():
                    continue
                cookies = await browser.cookies.get_all()
                jar = {
                    c.name: c.value
                    for c in cookies
                    if c.name in ("cf_clearance", "PHPSESSID")
                }
                if "cf_clearance" in jar:
                    user_agent = await page.evaluate("navigator.userAgent")
                    return {
                        "cookies": jar,
                        "user_agent": user_agent,
                        "ts": time.time(),
                    }
            return None
        finally:
            try:
                browser.stop()
            except Exception:
                pass

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        state: Optional[Dict[str, Any]] = loop.run_until_complete(_run())
    finally:
        asyncio.set_event_loop(None)
        loop.close()

    if not state:
        raise NetworkError(
            f"Could not solve the Cloudflare challenge within {timeout}s."
        )
    return state


def _solve_challenge_with_browser(url: str, timeout: int) -> Dict[str, Any]:
    """Run the browser solver in a dedicated thread.

    nodriver relies on asyncio; isolating it in its own thread with a fresh
    event loop keeps it from clashing with any event loop already running in
    the caller's thread (e.g. notebooks or async apps).
    """
    result: Dict[str, Any] = {}

    def _worker() -> None:
        try:
            result["state"] = _browser_solve(url, timeout)
        except BaseException as exc:  # noqa: BLE001 - propagated below
            result["error"] = exc

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join(timeout + 60)

    if "error" in result:
        raise result["error"]
    if "state" not in result:
        raise NetworkError("Timed out launching the browser to solve Cloudflare.")
    state: Dict[str, Any] = result["state"]
    return state


def _refresh_clearance(url: str) -> None:
    global _last_refresh
    with _refresh_lock:
        # Another caller may have just refreshed while we waited on the lock.
        if time.time() - _last_refresh < REFRESH_COOLDOWN:
            cached = _load_state()
            if cached:
                _apply_state(_get_session(), cached)
                return

        state = _solve_challenge_with_browser(url, BROWSER_TIMEOUT)
        _save_state(state)
        _apply_state(_get_session(), state)
        _last_refresh = time.time()


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def _raw_get(session: Any, url: str, **kwargs: Any) -> Any:
    try:
        return session.get(url, **kwargs)
    except cffi_requests.exceptions.RequestException as exc:
        raise NetworkError(f"HTTP request failed: {exc}") from exc


def get(url: str, **kwargs: Any) -> Any:
    """Perform a GET request, transparently clearing Cloudflare when needed.

    Do NOT pass a custom ``User-Agent`` header -- it must match the browser that
    solved the Cloudflare challenge, which this module manages automatically.

    Raises:
        NetworkError: On connection failure, an unsolved Cloudflare challenge,
            or an HTTP error status.
    """
    response = _raw_get(_get_session(), url, **kwargs)

    if _is_cf_challenge(response):
        target = str(getattr(response, "url", "") or url)
        _refresh_clearance(target)
        response = _raw_get(_get_session(), url, **kwargs)
        if _is_cf_challenge(response):
            raise NetworkError(
                "Cloudflare challenge could not be solved for this request."
            )

    try:
        response.raise_for_status()
    except cffi_requests.exceptions.RequestException as exc:
        raise NetworkError(f"HTTP {response.status_code} error: {exc}") from exc

    return response
