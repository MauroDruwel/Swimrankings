"""
Core Athlete class for individual athlete data and details.
"""

from datetime import datetime
from typing import Dict, Any

import requests
from bs4 import BeautifulSoup

from .models import AthleteDetails
from .parsers import parse_personal_bests, parse_times_table
from .utils import parse_profile_info, is_valid_time
from .exceptions import NetworkError, ParseError


class Athlete:
    """
    Represents a single athlete with their information from swimrankings.net.
    
    Attributes:
        athlete_id (int): Unique athlete identifier
        full_name (str): Full name in "Last, First" format
        first_name (str): First name
        last_name (str): Last name
        birth_year (int): Birth year
        gender (str): Gender ("male" or "female")
        country (str): Country code (e.g., "BEL")
        club (str): Club name
        profile_url (str): URL to athlete's profile page
    """

    def __init__(
        self,
        athlete_id: int,
        full_name: str,
        birth_year: int,
        gender: str,
        country: str,
        club: str,
        profile_url: str,
    ) -> None:
        """
        Initialize an Athlete instance.
        
        Args:
            athlete_id: Unique athlete identifier
            full_name: Full name in "Last, First" format
            birth_year: Birth year
            gender: Gender ("male" or "female")
            country: Country code
            club: Club name  
            profile_url: URL to athlete's profile page
        """
        self.athlete_id = athlete_id
        self.full_name = full_name
        self.birth_year = birth_year
        self.gender = gender
        self.country = country
        self.club = club
        self.profile_url = profile_url

    @property
    def first_name(self) -> str:
        """Extract first name from full name."""
        if ", " in self.full_name:
            return self.full_name.split(", ", 1)[1]
        return ""

    @property
    def last_name(self) -> str:
        """Extract last name from full name."""
        if ", " in self.full_name:
            return self.full_name.split(", ", 1)[0]
        return self.full_name

    def __str__(self) -> str:
        """String representation of the athlete."""
        return f"{self.full_name} ({self.birth_year}) - {self.country}"

    def __repr__(self) -> str:
        """Detailed string representation of the athlete."""
        return (
            f"Athlete(id={self.athlete_id}, name='{self.full_name}', "
            f"birth_year={self.birth_year}, gender='{self.gender}', "
            f"country='{self.country}', club='{self.club}')"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality based on athlete ID."""
        if not isinstance(other, Athlete):
            return NotImplemented
        return self.athlete_id == other.athlete_id

    def __hash__(self) -> int:
        """Hash based on athlete ID."""
        return hash(self.athlete_id)

    def get_details(self, timeout: int = 30) -> AthleteDetails:
        """
        Fetch detailed information about the athlete including personal bests.
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            AthleteDetails object containing personal bests and profile info
            
        Raises:
            NetworkError: If there's a network connection issue
            ParseError: If the response cannot be parsed
        """
        try:
            response = requests.get(
                self.profile_url,
                timeout=timeout,
                headers={
                    "User-Agent": "SwimRankings Python Library/0.1.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                }
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Failed to fetch athlete details: {e}")

        try:
            return self._parse_athlete_details(response.text)
        except Exception as e:
            raise ParseError(f"Failed to parse athlete details: {e}")

    def _parse_athlete_details(self, html: str) -> AthleteDetails:
        """
        Parse the athlete detail page HTML to extract personal bests and profile info.
        
        Args:
            html: HTML content from the athlete detail page
            
        Returns:
            AthleteDetails object with parsed information
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Parse personal bests
        personal_bests = parse_personal_bests(soup)
        
        # Parse additional profile information
        profile_info = parse_profile_info(soup)
        
        return AthleteDetails(
            athlete_id=self.athlete_id,
            personal_bests=personal_bests,
            profile_info=profile_info,
            last_updated=datetime.now()
        )

    # Backwards compatibility methods for tests
    def _is_valid_time(self, time_str: str) -> bool:
        """Backwards compatibility wrapper for is_valid_time utility function."""
        return is_valid_time(time_str)

    def _parse_times_table(self, table):
        """Backwards compatibility wrapper for parse_times_table function."""
        return parse_times_table(table)

    def _parse_profile_info(self, soup):
        """Backwards compatibility wrapper for parse_profile_info function."""
        return parse_profile_info(soup)
