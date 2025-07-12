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
