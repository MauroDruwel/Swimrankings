"""
Custom exceptions for the SwimRankings library.
"""


class SwimRankingsError(Exception):
    """Base exception for all SwimRankings library errors."""
    pass


class NetworkError(SwimRankingsError):
    """Raised when there's a network-related error."""
    pass


class AthleteNotFoundError(SwimRankingsError):
    """Raised when no athletes are found for the given search criteria."""
    pass


class InvalidGenderError(SwimRankingsError):
    """Raised when an invalid gender value is provided."""
    pass


class ParseError(SwimRankingsError):
    """Raised when there's an error parsing the response from swimrankings.net."""
    pass
