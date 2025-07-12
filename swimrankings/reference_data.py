"""
Reference data module for SwimRankings library.

This module provides functions to fetch and cache reference data from swimrankings.net,
including country codes and time period selections.
"""

from typing import Dict, List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
import re
from .exceptions import NetworkError, ParseError


def fetch_countries() -> Dict[str, Tuple[str, str]]:
    """
    Fetch available countries/nations from swimrankings.net.
    
    Returns:
        Dict mapping nation ID to tuple of (code, name)
        Example: {"43": ("BEL", "Belgium"), "273": ("NED", "Netherlands")}
        
    Raises:
        NetworkError: If there's a network connection issue
        ParseError: If the response cannot be parsed
    """
    url = "https://www.swimrankings.net/index.php?page=meetSelect&nationId=0&selectPage=RECENT"
    
    try:
        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": "SwimRankings Python Library/0.1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise NetworkError(f"Failed to fetch countries data: {e}")

    try:
        return _parse_countries(response.text)
    except Exception as e:
        raise ParseError(f"Failed to parse countries data: {e}")


def fetch_time_periods() -> Dict[str, str]:
    """
    Fetch available time periods/month codes from swimrankings.net.
    
    Returns:
        Dict mapping period code to display name
        Example: {"2025_m07": "2025 - juli", "2024_m12": "2024 - december"}
        
    Raises:
        NetworkError: If there's a network connection issue
        ParseError: If the response cannot be parsed
    """
    url = "https://www.swimrankings.net/index.php?page=meetSelect&nationId=0&selectPage=RECENT"
    
    try:
        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": "SwimRankings Python Library/0.1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise NetworkError(f"Failed to fetch time periods data: {e}")

    try:
        return _parse_time_periods(response.text)
    except Exception as e:
        raise ParseError(f"Failed to parse time periods data: {e}")


def _parse_countries(html: str) -> Dict[str, Tuple[str, str]]:
    """
    Parse HTML to extract country/nation information.
    
    Args:
        html: HTML content from the meetSelect page
        
    Returns:
        Dict mapping nation ID to tuple of (code, name)
    """
    soup = BeautifulSoup(html, "lxml")
    countries = {}
    
    # Find the nation select dropdown
    nation_select = soup.find("select", {"name": "nationId"})
    if not nation_select:
        raise ParseError("Could not find nation select dropdown")
    
    options = nation_select.find_all("option")
    for option in options:
        value = option.get("value")
        text = option.get_text(strip=True)
        
        # Skip the "Wereldwijd" (worldwide) option
        if value == "$$$":
            continue
            
        # Parse the format "CODE  -  Country Name" (note multiple spaces)
        # Use regex to handle variable whitespace
        import re
        match = re.match(r'^([A-Z]{3})\s+-\s+(.+)$', text)
        if match:
            code = match.group(1).strip()
            name = match.group(2).strip()
            countries[value] = (code, name)
    
    return countries


def _parse_time_periods(html: str) -> Dict[str, str]:
    """
    Parse HTML to extract time period/month information.
    
    Args:
        html: HTML content from the meetSelect page
        
    Returns:
        Dict mapping period code to display name
    """
    soup = BeautifulSoup(html, "lxml")
    time_periods = {}
    
    # Find the selectPage dropdown
    select_page = soup.find("select", {"name": "selectPage"})
    if not select_page:
        raise ParseError("Could not find selectPage dropdown")
    
    options = select_page.find_all("option")
    for option in options:
        value = option.get("value")
        text = option.get_text(strip=True)
        
        # Skip non-time period options
        if not value or value in ["RECENT", "BYTYPE"]:
            continue
            
        # Only include options that look like time periods (contain year and month/period)
        if re.match(r"\d{4}_", value):
            time_periods[value] = text
    
    return time_periods


def get_country_code(nation_id: str) -> Optional[str]:
    """
    Get country code for a given nation ID.
    
    Args:
        nation_id: The nation ID (e.g., "43" for Belgium)
        
    Returns:
        Country code (e.g., "BEL") or None if not found
    """
    try:
        countries = fetch_countries()
        if nation_id in countries:
            return countries[nation_id][0]
    except (NetworkError, ParseError):
        pass
    return None


def get_country_name(nation_id: str) -> Optional[str]:
    """
    Get country name for a given nation ID.
    
    Args:
        nation_id: The nation ID (e.g., "43" for Belgium)
        
    Returns:
        Country name (e.g., "Belgium") or None if not found
    """
    try:
        countries = fetch_countries()
        if nation_id in countries:
            return countries[nation_id][1]
    except (NetworkError, ParseError):
        pass
    return None


def find_nation_id_by_code(country_code: str) -> Optional[str]:
    """
    Find nation ID by country code.
    
    Args:
        country_code: The country code (e.g., "BEL")
        
    Returns:
        Nation ID (e.g., "43") or None if not found
    """
    try:
        countries = fetch_countries()
        for nation_id, (code, name) in countries.items():
            if code.upper() == country_code.upper():
                return nation_id
    except (NetworkError, ParseError):
        pass
    return None


def get_available_years() -> List[int]:
    """
    Get list of available years from time periods.
    
    Returns:
        Sorted list of available years
    """
    try:
        time_periods = fetch_time_periods()
        years = set()
        
        for period_code in time_periods.keys():
            # Extract year from codes like "2025_m07" or "1999_1999"
            match = re.match(r"(\d{4})_", period_code)
            if match:
                years.add(int(match.group(1)))
        
        return sorted(years, reverse=True)
    except (NetworkError, ParseError):
        return []


def get_months_for_year(year: int) -> Dict[str, str]:
    """
    Get available months for a specific year.
    
    Args:
        year: The year to get months for
        
    Returns:
        Dict mapping month code to display name
        Example: {"2025_m07": "2025 - juli"}
    """
    try:
        time_periods = fetch_time_periods()
        year_months = {}
        
        for period_code, display_name in time_periods.items():
            if period_code.startswith(f"{year}_m"):
                year_months[period_code] = display_name
        
        return year_months
    except (NetworkError, ParseError):
        return {}


# Cache variables for frequently accessed data
_countries_cache: Optional[Dict[str, Tuple[str, str]]] = None
_time_periods_cache: Optional[Dict[str, str]] = None


def get_cached_countries() -> Dict[str, Tuple[str, str]]:
    """
    Get countries data with caching.
    
    Returns:
        Dict mapping nation ID to tuple of (code, name)
    """
    global _countries_cache
    if _countries_cache is None:
        _countries_cache = fetch_countries()
    return _countries_cache


def get_cached_time_periods() -> Dict[str, str]:
    """
    Get time periods data with caching.
    
    Returns:
        Dict mapping period code to display name
    """
    global _time_periods_cache
    if _time_periods_cache is None:
        _time_periods_cache = fetch_time_periods()
    return _time_periods_cache


def clear_cache():
    """Clear all cached reference data."""
    global _countries_cache, _time_periods_cache
    _countries_cache = None
    _time_periods_cache = None
