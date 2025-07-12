"""
Athletes module for searching and managing swimmer athlete data.
"""

import re
from typing import List, Optional, Iterator, Union, Dict, Any
from urllib.parse import urljoin
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag

from .exceptions import (
    NetworkError,
    AthleteNotFoundError,
    InvalidGenderError,
    ParseError,
)


@dataclass
class PersonalBest:
    """
    Represents a personal best time for a specific event.
    
    Attributes:
        event (str): Event name (e.g., "50 Free")
        course (str): Course type ("SCM", "LCM", "SCY")
        time (str): Time in format (e.g., "24.50")
        date (Optional[str]): Date when the time was achieved
        meet (Optional[str]): Meet name where the time was achieved
        location (Optional[str]): Location where the time was achieved
    """
    event: str
    course: str
    time: str
    date: Optional[str] = None
    meet: Optional[str] = None
    location: Optional[str] = None


@dataclass
class AthleteDetails:
    """
    Detailed information about an athlete.
    
    Attributes:
        athlete_id (int): Unique athlete identifier
        personal_bests (List[PersonalBest]): List of personal best times
        profile_info (Dict[str, Any]): Additional profile information
        last_updated (datetime): When the details were last fetched
    """
    athlete_id: int
    personal_bests: List[PersonalBest]
    profile_info: Dict[str, Any]
    last_updated: datetime


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
        personal_bests = self._parse_personal_bests(soup)
        
        # Parse additional profile information
        profile_info = self._parse_profile_info(soup)
        
        return AthleteDetails(
            athlete_id=self.athlete_id,
            personal_bests=personal_bests,
            profile_info=profile_info,
            last_updated=datetime.now()
        )

    def _parse_personal_bests(self, soup: BeautifulSoup) -> List[PersonalBest]:
        """
        Parse personal best times from the athlete detail page.
        
        Args:
            soup: BeautifulSoup object of the athlete detail page
            
        Returns:
            List of PersonalBest objects
        """
        personal_bests = []
        
        # Look for the specific table containing personal best times
        # Based on the provided HTML, look for tables with class "athleteBest"
        best_table = soup.find("table", class_="athleteBest")
        
        if best_table and isinstance(best_table, Tag):
            personal_bests.extend(self._parse_athlete_best_table(best_table))
        
        # Also try generic table parsing as fallback
        tables = soup.find_all("table")
        
        for table in tables:
            if table == best_table:
                continue  # Skip already parsed table
                
            # Look for headers that indicate this is a results/times table
            headers = table.find_all("th")
            if not headers:
                continue
                
            header_texts = [th.get_text(strip=True).lower() for th in headers if isinstance(th, Tag)]
            
            # Check if this looks like a times table
            if any(keyword in " ".join(header_texts) for keyword in ["time", "event", "date", "meet"]):
                if isinstance(table, Tag):
                    personal_bests.extend(self._parse_times_table(table))
        
        return personal_bests

    def _parse_athlete_best_table(self, table: Tag) -> List[PersonalBest]:
        """
        Parse the athleteBest table specifically from swimrankings.net.
        
        Args:
            table: BeautifulSoup Tag representing the athleteBest table
            
        Returns:
            List of PersonalBest objects
        """
        personal_bests: List[PersonalBest] = []
        
        # Skip the header row and parse data rows
        all_rows = table.find_all("tr")
        rows = [row for row in all_rows[1:] if isinstance(row, Tag)]  # Skip header row and filter Tags
        
        for row in rows:
            try:
                cells = row.find_all("td")
                tag_cells = [cell for cell in cells if isinstance(cell, Tag)]
                if len(tag_cells) < 7:  # Expect at least 7 columns based on HTML structure
                    continue
                
                # Extract data based on the HTML structure provided
                event_cell = tag_cells[0]  # Event column
                course_cell = tag_cells[1]  # Course column (Baan)
                time_cell = tag_cells[2]   # Time column (Tijd)
                date_cell = tag_cells[4]   # Date column (Datum)
                city_cell = tag_cells[5]   # City column (Plaats)
                meet_cell = tag_cells[6]   # Meet column (Wedstrijd)
                
                # Extract text content
                event = event_cell.get_text(strip=True)
                course = course_cell.get_text(strip=True)
                time = time_cell.get_text(strip=True)
                date = date_cell.get_text(strip=True) if date_cell else None
                city = city_cell.get_text(strip=True) if city_cell else None
                meet = meet_cell.get_text(strip=True) if meet_cell else None
                
                # Clean up the data
                event = re.sub(r'\s+', ' ', event).strip()
                time = re.sub(r'\s+', ' ', time).strip()
                course = re.sub(r'\s+', ' ', course).strip()
                
                # Map course types from Dutch to standard abbreviations
                course_mapping = {
                    "50m": "LCM",  # Long Course Meters
                    "25m": "SCM",  # Short Course Meters
                }
                course = course_mapping.get(course, course)
                
                # Validate that we have essential data
                if event and time and self._is_valid_time(time):
                    personal_best = PersonalBest(
                        event=event,
                        course=course,
                        time=time,
                        date=date if date and date != "-" else None,
                        meet=meet if meet and meet != "-" else None,
                        location=city if city and city != "-" else None
                    )
                    personal_bests.append(personal_best)
                    
            except (IndexError, AttributeError) as e:
                # Skip malformed rows
                continue
        
        return personal_bests

    def _parse_times_table(self, table: Tag) -> List[PersonalBest]:
        """
        Parse a table containing time results.
        
        Args:
            table: BeautifulSoup Tag representing a table
            
        Returns:
            List of PersonalBest objects
        """
        personal_bests: List[PersonalBest] = []
        
        # Get header row to understand column structure
        header_row = table.find("tr")
        if not header_row or not isinstance(header_row, Tag):
            return personal_bests
            
        header_elements = header_row.find_all(["th", "td"])
        headers = [th.get_text(strip=True).lower() for th in header_elements if isinstance(th, Tag)]
        
        # Find column indices
        event_idx = next((i for i, h in enumerate(headers) if "event" in h), None)
        time_idx = next((i for i, h in enumerate(headers) if "time" in h), None)
        course_idx = next((i for i, h in enumerate(headers) if "course" in h or "pool" in h), None)
        date_idx = next((i for i, h in enumerate(headers) if "date" in h), None)
        meet_idx = next((i for i, h in enumerate(headers) if "meet" in h or "competition" in h), None)
        location_idx = next((i for i, h in enumerate(headers) if "location" in h or "place" in h), None)
        
        # Parse data rows
        all_rows = table.find_all("tr")
        rows = [row for row in all_rows[1:] if isinstance(row, Tag)]  # Skip header row and filter Tags
        
        for row in rows:
            all_cells = row.find_all(["td", "th"])
            cells = [cell for cell in all_cells if isinstance(cell, Tag)]
            if len(cells) < 2:  # Need at least event and time
                continue
                
            try:
                event = cells[event_idx].get_text(strip=True) if event_idx is not None and event_idx < len(cells) else ""
                time = cells[time_idx].get_text(strip=True) if time_idx is not None and time_idx < len(cells) else ""
                course = cells[course_idx].get_text(strip=True) if course_idx is not None and course_idx < len(cells) else ""
                date = cells[date_idx].get_text(strip=True) if date_idx is not None and date_idx < len(cells) else None
                meet = cells[meet_idx].get_text(strip=True) if meet_idx is not None and meet_idx < len(cells) else None
                location = cells[location_idx].get_text(strip=True) if location_idx is not None and location_idx < len(cells) else None
                
                # Clean up the data
                event = re.sub(r'\s+', ' ', event).strip()
                time = re.sub(r'\s+', ' ', time).strip()
                course = re.sub(r'\s+', ' ', course).strip()
                
                # Validate that we have essential data
                if event and time and self._is_valid_time(time):
                    personal_best = PersonalBest(
                        event=event,
                        course=course or "Unknown",
                        time=time,
                        date=date if date and date != "-" else None,
                        meet=meet if meet and meet != "-" else None,
                        location=location if location and location != "-" else None
                    )
                    personal_bests.append(personal_best)
                    
            except (IndexError, AttributeError):
                continue
        
        return personal_bests

    def _parse_times_section(self, section: Tag) -> List[PersonalBest]:
        """
        Parse a section/div containing time results.
        
        Args:
            section: BeautifulSoup Tag representing a section
            
        Returns:
            List of PersonalBest objects
        """
        personal_bests: List[PersonalBest] = []
        
        # Look for patterns in the text that might indicate times
        text = section.get_text()
        
        # Common patterns for swimming times (e.g., "24.50", "1:24.50", "2:24.50.0")
        time_pattern = r'\b(?:\d{1,2}:)?(?:\d{1,2}:)?\d{1,2}\.\d{2}(?:\.\d{1,2})?\b'
        times = re.findall(time_pattern, text)
        
        # This is a basic implementation - in practice, you'd need more sophisticated parsing
        # based on the actual HTML structure of the athlete detail page
        
        return personal_bests

    def _parse_profile_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Parse additional profile information from the athlete detail page.
        
        Args:
            soup: BeautifulSoup object of the athlete detail page
            
        Returns:
            Dictionary containing profile information
        """
        profile_info = {}
        
        # Parse athlete header information
        header_div = soup.find("div", id="header_athleteDetail")
        if header_div and isinstance(header_div, Tag):
            # Extract athlete info from the header
            athleteinfo_div = header_div.find("div", id="athleteinfo")
            if athleteinfo_div and isinstance(athleteinfo_div, Tag):
                # Extract name and birth year with gender
                name_div = athleteinfo_div.find("div", id="name")
                if name_div and isinstance(name_div, Tag):
                    name_text = name_div.get_text(strip=True)
                    profile_info["header_name"] = name_text
                
                # Extract nation and club
                nationclub_div = athleteinfo_div.find("div", id="nationclub")
                if nationclub_div and isinstance(nationclub_div, Tag):
                    nationclub_text = nationclub_div.get_text(strip=True)
                    lines = [line.strip() for line in nationclub_text.split('\n') if line.strip()]
                    
                    for line in lines:
                        if " - " in line and len(line.split(" - ")) == 2:
                            country_code, country_name = line.split(" - ", 1)
                            profile_info["country_code"] = country_code.strip()
                            profile_info["country_name"] = country_name.strip()
                        elif line and not line.startswith("BEL"):  # Assuming BEL is country code
                            profile_info["club_name"] = line.strip()
        
        # Look for profile sections, info tables, etc.
        info_tables = soup.find_all("table", class_=re.compile(r".*info.*|.*profile.*|.*athlete.*", re.I))
        
        for table in info_tables:
            if isinstance(table, Tag):
                all_rows = table.find_all("tr")
                rows = [row for row in all_rows if isinstance(row, Tag)]
                for row in rows:
                    all_cells = row.find_all(["td", "th"])
                    cells = [cell for cell in all_cells if isinstance(cell, Tag)]
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            profile_info[key] = value
        
        # Look for other structured data
        divs = soup.find_all("div", class_=re.compile(r".*info.*|.*detail.*", re.I))
        for div in divs:
            if isinstance(div, Tag):
                # Extract any structured information
                all_labels = div.find_all(["strong", "b", "label"])
                labels = [label for label in all_labels if isinstance(label, Tag)]
                for label in labels:
                    text = label.get_text(strip=True)
                    if text and ":" in text:
                        key, value = text.split(":", 1)
                        profile_info[key.strip().lower()] = value.strip()
        
        # Extract photo URL if available
        photo_div = soup.find("div", id="photo")
        if photo_div and isinstance(photo_div, Tag):
            img = photo_div.find("img")
            if img and isinstance(img, Tag):
                src = img.get("src")
                if src and isinstance(src, str):
                    profile_info["photo_url"] = src
        
        return profile_info

    def _is_valid_time(self, time_str: str) -> bool:
        """
        Check if a string represents a valid swimming time.
        
        Args:
            time_str: String to validate
            
        Returns:
            True if the string looks like a valid swimming time
        """
        # Basic validation for swimming time format
        # Formats: MM.SS, M:SS.SS, MM:SS.SS, H:MM:SS.SS
        time_pattern = r'^\d{1,2}:\d{2}:\d{2}\.\d{2}$|^\d{1,2}:\d{2}\.\d{2}$|^\d{1,2}\.\d{2}$'
        return bool(re.match(time_pattern, time_str.strip()))


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
