"""
Parsing functions for athlete best times and results.
"""

import re
from typing import List
from bs4 import BeautifulSoup, Tag

from .models import PersonalBest
from .utils import is_valid_time


def parse_personal_bests(soup: BeautifulSoup) -> List[PersonalBest]:
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
        personal_bests.extend(parse_athlete_best_table(best_table))
    
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
                personal_bests.extend(parse_times_table(table))
    
    return personal_bests


def parse_athlete_best_table(table: Tag) -> List[PersonalBest]:
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
            if event and time and is_valid_time(time):
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


def parse_times_table(table: Tag) -> List[PersonalBest]:
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
            if event and time and is_valid_time(time):
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
