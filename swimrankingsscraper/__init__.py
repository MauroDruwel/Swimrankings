"""
SwimrankingsScraper: A web scraper for Swimrankings.net to retrieve information about athletes, meets, and results.

Usage:
    from swimrankingsscraper import SwimrankingsScraper
    
    scraper = SwimrankingsScraper()
    athlete = scraper.get_athlete('4292888')
    personal_bests = athlete.list_personal_bests()
"""

from .scraper import SwimrankingsScraper
from .athlete import Athlete
from .meet import Meet
from .result import Result
from .meets import Meets
from .club import Club
from .session_manager import SessionManager
from .utils import convert_time

__all__ = [
    'SwimrankingsScraper',
    'Athlete',
    'Meet',
    'Result',
    'Meets',
    'Club',
    'SessionManager',
    'convert_time'
]

__version__ = '1.0.0'