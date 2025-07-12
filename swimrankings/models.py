"""
Data models for athlete information.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


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
