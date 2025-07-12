"""
Athletes module for searching and managing swimmer athlete data.

This module maintains backwards compatibility by re-exporting classes from the new modular structure.
"""

# Import from new modular structure
from .models import PersonalBest, AthleteDetails
from .athlete import Athlete
from .search import Athletes

# For backwards compatibility with tests, import modules that tests may try to patch
import requests
from bs4 import BeautifulSoup
from . import utils
from . import parsers

# Maintain backwards compatibility by exporting all classes
__all__ = ["PersonalBest", "AthleteDetails", "Athlete", "Athletes"]
