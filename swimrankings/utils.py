"""
Utility functions for parsing swimming data.
"""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup, Tag

from .models import PersonalBest


def is_valid_time(time_str: str) -> bool:
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


def parse_profile_info(soup: BeautifulSoup) -> Dict[str, Any]:
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
