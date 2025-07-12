"""
SwimRankings Python Library

A modern Python library for interacting with swimrankings.net
"""

from .athletes import Athletes, Athlete, PersonalBest, AthleteDetails
from .exceptions import SwimRankingsError, AthleteNotFoundError, NetworkError

__version__ = "0.1.0"
__author__ = "Mauro Druwel"
__email__ = "your.email@example.com"

__all__ = [
    "Athletes",
    "Athlete", 
    "PersonalBest",
    "AthleteDetails",
    "SwimRankingsError",
    "AthleteNotFoundError",
    "NetworkError",
]
