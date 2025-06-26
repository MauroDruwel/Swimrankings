"""
Main SwimrankingsScraper class for accessing all functionality.
"""

from .session_manager import SessionManager
from .athlete import Athlete
from .meet import Meet
from .result import Result
from .meets import Meets
from .club import Club


class SwimrankingsScraper:
    """
    Main class for the Swimrankings web scraper.

    Attributes:
    - `sessionManager` (SessionManager): An instance of SessionManager for managing HTTP requests.

    Methods:
    - `__init__()`: Initializes the SwimrankingsScraper with the base URL and a requests session.
    - `get_athlete(athlete_id)`: Retrieves an Athlete instance for the specified athlete ID.
    - `get_meet(meet_id)`: Retrieves a Meet instance for the specified meet ID.
    - `get_results(result_id)`: Retrieves a Result instance for the specified result ID.
    - `get_meets()`: Retrieves a Meets instance.
    - `get_club(club_id)`: Retrieves a Club instance for the specified club ID.

    Usage Example:
    ```python
    scraper = SwimrankingsScraper()
    athlete_instance = scraper.get_athlete('4292888')
    meet_instance = scraper.get_meet('123456')
    result_instance = scraper.get_results('789012')
    meets_instance = scraper.get_meets()
    club_instance = scraper.get_club('987654')
    ```

    Details:
    - The class provides methods to obtain instances for Athlete, Meet, Result, Meets, and Club.
    - These instances allow accessing various functionalities related to athletes, meets, and results.
    - The SessionManager is used for handling HTTP requests.
    - Instantiate this class to start using the Swimrankings web scraper functionalities.
    """

    def __init__(self):
        """
        Initializes the SwimrankingsScraper with the base URL and a requests session.
        """
        self.sessionManager = SessionManager()

    def get_athlete(self, athlete_id):
        """
        Retrieves an Athlete instance for the specified athlete ID.

        Parameters:
        - `athlete_id` (str): The ID of the athlete.

        Returns:
        - `Athlete`: An Athlete instance.
        """
        return Athlete(athlete_id, self.sessionManager)

    def get_meet(self, meet_id):
        """
        Retrieves a Meet instance for the specified meet ID.

        Parameters:
        - `meet_id` (str): The ID of the meet.

        Returns:
        - `Meet`: A Meet instance.
        """
        return Meet(meet_id, self.sessionManager)

    def get_result(self, result_id):
        """
        Retrieves a Result instance for the specified result ID.

        Parameters:
        - `result_id` (str): The ID of the result.

        Returns:
        - `Result`: A Result instance.
        """
        return Result(result_id, self.sessionManager)

    def get_meets(self):
        """
        Retrieves a Meets instance.

        Returns:
        - `Meets`: A Meets instance.
        """
        return Meets(self.sessionManager)

    def get_club(self, club_id):
        """
        Retrieves a Club instance for the specified club ID.

        Parameters:
        - `club_id` (str): The ID of the club.

        Returns:
        - `Club`: A Club instance.
        """
        return Club(club_id, self.sessionManager)
