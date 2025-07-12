"""
Athletes search class for finding athletes on swimrankings.net.
"""

import re
from typing import List, Optional, Iterator, Union, Dict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from .athlete import Athlete
from .exceptions import (
    NetworkError,
    AthleteNotFoundError,
    InvalidGenderError,
    ParseError,
)


class Athletes:
    """
    Class for searching athletes on swimrankings.net.
    
    Provides an iterable interface to search and access athlete data.
    """

    BASE_URL = "https://www.swimrankings.net/index.php"
    
    # Gender mapping for API calls
    GENDER_MAP = {
        "all": -1,
        "male": 1, 
        "female": 2,
    }

    def __init__(
        self,
        name: str,
        gender: str = "all",
        club_id: int = -1,
        timeout: int = 30,
    ) -> None:
        """
        Initialize Athletes search.
        
        Args:
            name: Last name to search for
            gender: Gender filter - "all", "male", or "female"
            club_id: Club ID filter (-1 for all clubs)
            timeout: Request timeout in seconds
            
        Raises:
            InvalidGenderError: If gender is not valid
            NetworkError: If there's a network connection issue
            AthleteNotFoundError: If no athletes are found
        """
        self.name = name.strip()
        self.gender = gender.lower()
        self.club_id = club_id
        self.timeout = timeout
        self._athletes: List[Athlete] = []
        
        # Validate gender
        if self.gender not in self.GENDER_MAP:
            raise InvalidGenderError(
                f"Invalid gender '{gender}'. Must be one of: {', '.join(self.GENDER_MAP.keys())}"
            )
        
        # Perform the search
        self._search()

    def _search(self) -> None:
        """
        Perform the athlete search and populate the athletes list.
        
        Raises:
            NetworkError: If there's a network connection issue
            ParseError: If the response cannot be parsed
            AthleteNotFoundError: If no athletes are found
        """
        params: Dict[str, Union[str, int]] = {
            "internalRequest": "athleteFind",
            "athlete_clubId": self.club_id,
            "athlete_gender": self.GENDER_MAP[self.gender],
            "athlete_lastname": self.name,
            "athlete_firstname": "",
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout,
                headers={
                    "User-Agent": "SwimRankings Python Library/0.1.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                }
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Failed to fetch data from swimrankings.net: {e}")

        try:
            self._parse_response(response.text)
        except Exception as e:
            raise ParseError(f"Failed to parse response: {e}")

        if not self._athletes:
            raise AthleteNotFoundError(
                f"No athletes found for name '{self.name}' "
                f"with gender filter '{self.gender}'"
            )

    def _parse_response(self, html: str) -> None:
        """
        Parse the HTML response and extract athlete data.
        
        Args:
            html: HTML response from swimrankings.net
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Find the athlete search table
        table = soup.find("table", class_="athleteSearch")
        if not table or not isinstance(table, Tag):
            return

        # Find all athlete rows (skip the header row)
        all_rows = table.find_all("tr", class_=re.compile(r"athleteSearch\d+"))
        rows = [row for row in all_rows if isinstance(row, Tag)]
        
        for row in rows:
            athlete = self._parse_athlete_row(row)
            if athlete:
                self._athletes.append(athlete)

    def _parse_athlete_row(self, row: Tag) -> Optional[Athlete]:
        """
        Parse a single athlete row from the search results.
        
        Args:
            row: BeautifulSoup Tag representing a table row
            
        Returns:
            Athlete instance or None if parsing fails
        """
        try:
            # Find the name cell with the link
            name_cell = row.find("td", class_="name")
            if not name_cell or not isinstance(name_cell, Tag):
                return None
                
            link = name_cell.find("a")
            if not link or not isinstance(link, Tag):
                return None

            # Extract athlete ID from the href
            href_raw = link.get("href", "")
            href = href_raw if isinstance(href_raw, str) else ""
            athlete_id_match = re.search(r"athleteId=(\d+)", href)
            if not athlete_id_match:
                return None
            athlete_id = int(athlete_id_match.group(1))

            # Extract full name (remove <b> tags)
            full_name = link.get_text(strip=True)

            # Extract birth year
            date_cell = row.find("td", class_="date")
            birth_year = int(date_cell.get_text(strip=True)) if date_cell and isinstance(date_cell, Tag) else 0

            # Extract gender from image
            gender_img = row.find("img")
            gender = "unknown"
            if gender_img and isinstance(gender_img, Tag):
                src_raw = gender_img.get("src", "")
                src = src_raw if isinstance(src_raw, str) else ""
                if "gender1.png" in src:
                    gender = "male"
                elif "gender2.png" in src:
                    gender = "female"

            # Extract country code
            code_cell = row.find("td", class_="code")
            country = code_cell.get_text(strip=True) if code_cell and isinstance(code_cell, Tag) else ""

            # Extract club name
            club_cell = row.find("td", class_="club")
            club = club_cell.get_text(strip=True) if club_cell and isinstance(club_cell, Tag) else ""

            # Build full profile URL
            profile_url = urljoin(self.BASE_URL, href)

            return Athlete(
                athlete_id=athlete_id,
                full_name=full_name,
                birth_year=birth_year,
                gender=gender,
                country=country,
                club=club,
                profile_url=profile_url,
            )

        except (ValueError, AttributeError) as e:
            # Log the error in a real implementation
            return None

    def __iter__(self) -> Iterator[Athlete]:
        """Iterate over the athletes."""
        return iter(self._athletes)

    def __len__(self) -> int:
        """Return the number of athletes found."""
        return len(self._athletes)

    def __getitem__(self, index: Union[int, slice]) -> Union[Athlete, List[Athlete]]:
        """Get athlete(s) by index or slice."""
        return self._athletes[index]

    def __bool__(self) -> bool:
        """Return True if any athletes were found."""
        return bool(self._athletes)

    def filter_by_country(self, country_code: str) -> List[Athlete]:
        """
        Filter athletes by country code.
        
        Args:
            country_code: Country code to filter by (e.g., "BEL")
            
        Returns:
            List of athletes from the specified country
        """
        return [
            athlete for athlete in self._athletes 
            if athlete.country.upper() == country_code.upper()
        ]

    def filter_by_birth_year(self, min_year: int, max_year: Optional[int] = None) -> List[Athlete]:
        """
        Filter athletes by birth year range.
        
        Args:
            min_year: Minimum birth year (inclusive)
            max_year: Maximum birth year (inclusive). If None, uses min_year
            
        Returns:
            List of athletes within the birth year range
        """
        if max_year is None:
            max_year = min_year
            
        return [
            athlete for athlete in self._athletes
            if min_year <= athlete.birth_year <= max_year
        ]

    def filter_by_gender(self, gender: str) -> List[Athlete]:
        """
        Filter athletes by gender.
        
        Args:
            gender: Gender to filter by ("male" or "female")
            
        Returns:
            List of athletes of the specified gender
        """
        return [
            athlete for athlete in self._athletes
            if athlete.gender.lower() == gender.lower()
        ]

    def to_dict(self) -> List[dict]:
        """
        Convert all athletes to a list of dictionaries.
        
        Returns:
            List of dictionaries containing athlete data
        """
        return [
            {
                "athlete_id": athlete.athlete_id,
                "full_name": athlete.full_name,
                "first_name": athlete.first_name,
                "last_name": athlete.last_name,
                "birth_year": athlete.birth_year,
                "gender": athlete.gender,
                "country": athlete.country,
                "club": athlete.club,
                "profile_url": athlete.profile_url,
            }
            for athlete in self._athletes
        ]
