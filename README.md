# SwimRankings Python Library

A modern Python library for interacting with [swimrankings.net](https://www.swimrankings.net), providing easy access to athlete searches, personal bests, Swimrankings Member authentication, and reference data.

## Features

- 🏊‍♀️ **Athlete Search & Filtering**: Search athletes by last name, gender, and club ID, then filter by country, birth year, or gender
- 📈 **Detailed Data**: Fetch `AthleteDetails` with normalized `PersonalBest` records (`LCM` / `SCM`), meet metadata, and profile info
- 🔐 **Member Authentication**: Supports `swimrankings.login()`, `set_auth()`, environment variables, and per-call `auth=(email, password)`
- 🛡️ **Built-in Cloudflare Clearance**: Automatically solves Cloudflare's challenge locally via Chrome/`nodriver` and caches clearance for fast `curl_cffi` requests
- 🌍 **Reference Data**: Look up and cache countries/nation IDs and historical meet time periods
- 📊 **Type Hints**: Full type annotation support (`mypy`-checked) for better IDE integration

## Installation

```bash
pip install swimrankings
```

### Cloudflare requirement

swimrankings.net is protected by Cloudflare's "Just a moment..." challenge. To
get past it, this library solves the challenge **once** using a real local
Chrome/Chromium browser (driven by [`nodriver`](https://github.com/ultrafunkamsterdam/nodriver)),
then reuses the resulting clearance for fast `curl_cffi` requests. The clearance
is cached on disk (`~/.cache/swimrankings/`) and refreshed automatically when it
expires. No third-party services, accounts, or API keys are involved.

Requirements:

- **Chrome or Chromium** installed locally.
- On a headless server (no display), install the system **`xvfb`** package — the
  challenge cannot be solved with headless Chrome, so a virtual display is used
  automatically via `pyvirtualdisplay`:

  ```bash
  sudo apt-get install -y xvfb chromium
  ```

The first request in a fresh environment is slower (it launches the browser);
subsequent requests use the cached clearance and are fast.

Optional environment variables:

- `SWIMRANKINGS_BROWSER_PATH` — path to a specific Chrome/Chromium binary.
- `SWIMRANKINGS_CACHE_DIR` — override the clearance cache directory (`~/.cache/swimrankings/` by default).
- `DISPLAY` — X display used by the browser; on headless Linux a virtual display is started automatically when this is unset.
- `SWIMRANKINGS_USERNAME` / `SWIMRANKINGS_PASSWORD` — credentials for a free Swimrankings Member account. `SWIMRANKINGS_EMAIL` is accepted as an alias for `SWIMRANKINGS_USERNAME`.

### Authentication (Swimrankings Member)

On [swimrankings.net](https://www.swimrankings.net), most athlete detail pages (`get_details()`) return `HTTP 401` (`Basic realm="Swimrankings Member"`) when requested anonymously, while some profiles remain publicly accessible without authentication.

When accessing an athlete profile that requires authentication without credentials, `AuthenticationError` is raised. You can authenticate using a Swimrankings Member account via any of the following methods:

**1. Using `swimrankings.login()` (recommended):**

```python
import swimrankings

# Authenticate once in your session
swimrankings.login("your_email@example.com", "your_password")

athletes = swimrankings.Athletes(name="Marchand")
details = athletes[0].get_details()
```

**2. Using environment variables:**

```bash
export SWIMRANKINGS_USERNAME="your_email@example.com"
export SWIMRANKINGS_PASSWORD="your_password"
```

```python
import swimrankings

athletes = swimrankings.Athletes(name="Marchand")
details = athletes[0].get_details()
```

**3. Passing credentials directly:**

```python
from swimrankings import Athletes

# Pass credentials to search (automatically propagated to athletes)
athletes = Athletes(name="Marchand", auth=("your_email@example.com", "your_password"))
details = athletes[0].get_details()

# Or pass directly when fetching details
details = athletes[0].get_details(auth=("your_email@example.com", "your_password"))
```

**4. Storing credentials with `set_auth()`:**

```python
import swimrankings

swimrankings.set_auth("your_email@example.com", "your_password")
print(swimrankings.get_auth())  # ('your_email@example.com', 'your_password')

# Clear stored credentials again
swimrankings.set_auth(None, None)
```

`login(username, password, timeout=30)` submits the web login form, returns `True` on
success and raises `AuthenticationError` for invalid credentials. `get_details(timeout=30,
auth=None)` accepts a per-call timeout and credentials tuple that override the athlete's
stored credentials.

## Quick Start

```python
import swimrankings
from swimrankings import Athletes, AuthenticationError

# Authenticate once for protected athlete detail pages
swimrankings.login("your_email@example.com", "your_password")

# Search for athletes by last name (optionally filter by gender or club_id)
athletes = Athletes(name="Druwel")
for athlete in athletes:
    print(f"{athlete.full_name} ({athlete.birth_year}) - {athlete.country}")

# Get detailed information including personal bests
athlete = athletes[0]
try:
    details = athlete.get_details()
    print(f"Personal bests: {len(details.personal_bests)}")
    for pb in details.personal_bests:
        print(f"  {pb.event} ({pb.course}): {pb.time}")
except AuthenticationError:
    print("Authentication required or invalid credentials")
```

## Documentation

📖 **[Complete Documentation](https://maurodruwel.be/Swimrankings)** — Full guides, examples, and API reference:

- **[Installation](https://maurodruwel.be/Swimrankings/installation)** — Python 3.10+, Chrome/Chromium & `xvfb` setup, environment variables
- **[Quick Start](https://maurodruwel.be/Swimrankings/quick-start)** — Searching, filtering, authentication, and fetching personal bests
- **[Examples](https://maurodruwel.be/Swimrankings/examples)** — Real-world authentication flows, LCM vs SCM comparison, reference data lookups, CSV/JSON/Pandas exports, and retry patterns
- **[Reference Data](https://maurodruwel.be/Swimrankings/reference-data)** — Country codes, nation IDs, and time periods with caching
- **[API Reference](https://maurodruwel.be/Swimrankings/api-reference)** — Signatures, data models, exceptions, and environment variables
- **[Error Handling](https://maurodruwel.be/Swimrankings/error-handling)** — Exception hierarchy and recovery strategies

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
