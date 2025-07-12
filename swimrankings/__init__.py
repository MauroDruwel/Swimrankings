"""
SwimRankings Python Library

A modern Python library for interacting with swimrankings.net
"""

from .athletes import Athletes, Athlete, PersonalBest, AthleteDetails
from .exceptions import SwimRankingsError, AthleteNotFoundError, NetworkError
from .reference_data import (
    fetch_countries,
    fetch_time_periods,
    get_country_code,
    get_country_name,
    find_nation_id_by_code,
    get_available_years,
    get_months_for_year,
    get_cached_countries,
    get_cached_time_periods,
    clear_cache
)

__version__ = "0.1.1"
__author__ = "Mauro Druwel"
__email__ = "mauro.druwel@gmail.com"

__all__ = [
    "Athletes",
    "Athlete", 
    "PersonalBest",
    "AthleteDetails",
    "SwimRankingsError",
    "AthleteNotFoundError",
    "NetworkError",
    "fetch_countries",
    "fetch_time_periods",
    "get_country_code",
    "get_country_name", 
    "find_nation_id_by_code",
    "get_available_years",
    "get_months_for_year",
    "get_cached_countries",
    "get_cached_time_periods",
    "clear_cache",
]
