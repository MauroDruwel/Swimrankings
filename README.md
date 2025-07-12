# SwimRankings Python Library

A modern Python library for interacting with [swimrankings.net](https://www.swimrankings.net), providing easy access to athlete data, search functionality, and more.

## Features

- 🏊‍♀️ **Athlete Search**: Search for athletes by name, gender, and other criteria
- 📈 **Detailed Data**: Fetch personal bests, profile information, and more
- 📊 **Type Hints**: Full type annotation support for better IDE experience
- 🔍 **Flexible Filtering**: Filter athletes by gender, country, club, etc.
- 🚀 **Async Support**: Coming soon!

## Documentation

📖 **[Full Documentation](docs/)** - Complete documentation with examples and guides

The documentation is built with [Nextra](https://nextra.site/) and includes:
- Installation guide
- Quick start tutorial
- Usage examples
- Error handling guide
- Contributing guidelines

### Running Documentation Locally

```bash
# Setup documentation (requires Node.js 16+)
python docs_setup.py setup

# Start documentation server
python docs_setup.py dev

# Open http://localhost:3000 in your browser
```

## Installation

```bash
pip install swimrankings
```

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

# Search for male athletes only
male_athletes = Athletes(name="Druwel", gender="male")

# Search for female athletes only  
female_athletes = Athletes(name="Druwel", gender="female")
```
### Athletes Class

The main class for searching athletes on swimrankings.net.

#### Constructor

```python
Athletes(name: str, gender: str = "all", club_id: int = -1)
```

**Parameters:**
- `name` (str): Last name to search for
- `gender` (str, optional): Gender filter - "all", "male", or "female". Default: "all"
- `club_id` (int, optional): Club ID filter. Default: -1 (all clubs)

#### Methods

- `__iter__()`: Iterate over found athletes
- `__len__()`: Get number of athletes found
- `__getitem__(index)`: Get athlete by index

### Athlete Class

Represents a single athlete with their information.

#### Properties

- `athlete_id` (int): Unique athlete identifier
- `full_name` (str): Full name (Last, First)
- `first_name` (str): First name
- `last_name` (str): Last name  
- `birth_year` (int): Birth year
- `gender` (str): Gender ("male" or "female")
- `country` (str): Country code
- `club` (str): Club name
- `profile_url` (str): URL to athlete's profile page

## Development

```bash
# Clone the repository
git clone https://github.com/MauroDruwel/Swimrankings.git
cd Swimrankings

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black swimrankings/

# Type checking
mypy swimrankings/
```

### CI/CD

This project includes comprehensive CI/CD workflows:

- 🧪 **Automated Testing**: Tests run on every commit across Python 3.8-3.12
- 📚 **Documentation Deployment**: Auto-deploys to GitHub Pages
- 📦 **PyPI Publishing**: Auto-publishes to PyPI on releases
- 📊 **Coverage Tracking**: Coverage reports uploaded to Codecov

See [CI_CD_SETUP.md](CI_CD_SETUP.md) for detailed setup instructions.

### Helper Scripts

- `python scripts/test_ci.py` - Run all CI checks locally
- `python scripts/prepare_release.py` - Prepare a new release

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
