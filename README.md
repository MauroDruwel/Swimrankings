# SwimRankings Python Library

A modern Python library for interacting with [swimrankings.net](https://www.swimrankings.net), providing easy access to athlete data, search functionality, and more.

## Features

- 🏊‍♀️ **Athlete Search**: Search for athletes by name, gender, and other criteria
- 📈 **Detailed Data**: Fetch personal bests, profile information, and more
- 📊 **Type Hints**: Full type annotation support for better IDE experience
- 🔍 **Flexible Filtering**: Filter athletes by gender, country, club, etc.
- 🚀 **Async Support**: Coming soon!

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
- `SWIMRANKINGS_CACHE_DIR` — override the clearance cache directory.

## Quick Start

```python
from swimrankings import Athletes

# Search for athletes by name
athletes = Athletes(name="Druwel")
for athlete in athletes:
    print(f"{athlete.full_name} ({athlete.birth_year}) - {athlete.country}")

# Get detailed information including personal bests
athlete = athletes[0]
details = athlete.get_details()

print(f"Personal bests: {len(details.personal_bests)}")
for pb in details.personal_bests:
    print(f"  {pb.event} ({pb.course}): {pb.time}")
```

## Documentation

📖 **[Complete Documentation](https://maurodruwel.be/Swimrankings)** - Full API reference, examples, and guides

For detailed usage examples, API reference, error handling, and contributing guidelines, please visit the complete documentation.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
