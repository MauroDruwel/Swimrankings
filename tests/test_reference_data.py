"""
Tests for reference_data module.
"""

import pytest
from unittest.mock import Mock
from swimrankings.reference_data import (
    fetch_countries,
    fetch_time_periods,
    get_country_code,
    get_country_name,
    find_nation_id_by_code,
    get_available_years,
    get_months_for_year,
)


@pytest.fixture(autouse=True)
def mock_reference_data_http(monkeypatch):
    """Mock HTTP responses for reference data tests to keep them deterministic and fast."""
    codes = [f"{chr(65 + i // 26)}{chr(65 + i % 26)}A" for i in range(150)]
    countries_html = "".join(
        f'<option value="{i+1000}">{code}  -  Country {code}</option>'
        for i, code in enumerate(codes)
    )
    countries_html += (
        '<option value="43">BEL  -  Belgium</option>'
        '<option value="378">USA  -  United States</option>'
        '<option value="273">NED  -  Netherlands</option>'
    )

    periods_html = ""
    for y in range(2000, 2026):
        for m in range(1, 13):
            periods_html += f'<option value="{y}_m{m:02d}">{y} - month {m:02d}</option>'

    html = f'<html><select name="nationId">{countries_html}</select><select name="selectPage">{periods_html}</select></html>'

    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = html

    monkeypatch.setattr("swimrankings.reference_data.http.get", lambda *a, **kw: mock_resp)


def test_fetch_countries():
    """Test fetching countries data."""
    countries = fetch_countries()
    
    # Should have many countries
    assert len(countries) > 100
    
    # Belgium should be there
    assert "43" in countries
    code, name = countries["43"]
    assert code == "BEL"
    assert name == "Belgium"
    
    # USA should be there
    assert "378" in countries
    code, name = countries["378"]
    assert code == "USA"
    assert name == "United States"


def test_fetch_time_periods():
    """Test fetching time periods data."""
    periods = fetch_time_periods()
    
    # Should have many time periods
    assert len(periods) > 200
    
    # Should contain recent months
    current_year_keys = [k for k in periods.keys() if k.startswith("2024_m")]
    assert len(current_year_keys) > 10


def test_country_utilities():
    """Test country utility functions."""
    # Test getting country name and code
    assert get_country_name("43") == "Belgium"
    assert get_country_code("43") == "BEL"
    
    # Test finding nation ID by code
    assert find_nation_id_by_code("BEL") == "43"
    assert find_nation_id_by_code("USA") == "378"
    assert find_nation_id_by_code("NED") == "273"
    
    # Test case insensitive
    assert find_nation_id_by_code("bel") == "43"
    assert find_nation_id_by_code("usa") == "378"


def test_year_utilities():
    """Test year-related utility functions."""
    years = get_available_years()
    
    # Should have many years
    assert len(years) > 20
    
    # Should be sorted in descending order
    assert years == sorted(years, reverse=True)
    
    # Should contain recent years
    assert 2024 in years
    assert 2023 in years
    
    # Test months for specific year
    months_2024 = get_months_for_year(2024)
    assert len(months_2024) >= 12  # Should have all months
    
    # Check specific month exists
    assert any("2024_m12" in code for code in months_2024.keys())


if __name__ == "__main__":
    # Run tests directly
    test_fetch_countries()
    print("✓ test_fetch_countries passed")
    
    test_fetch_time_periods()
    print("✓ test_fetch_time_periods passed")
    
    test_country_utilities()
    print("✓ test_country_utilities passed")
    
    test_year_utilities()
    print("✓ test_year_utilities passed")
    
    print("\nAll tests passed!")
