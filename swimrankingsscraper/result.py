"""
Result class for retrieving swimming result information.
"""

from .mixins import ScraperMixin


class Result(ScraperMixin):
    """
    Represents a swimming result and provides methods to retrieve information about the result.

    Attributes:
    - `result_id` (str): The ID of the result.
    - `sessionManager` (SessionManager): The SessionManager instance for making HTTP requests.
    - `update_interval` (int): The minimum time interval (in seconds) between consecutive updates.

    Methods:
    - `__init__(result_id, sessionManager, update_interval=60)`: Initializes the Result with a result ID and a requests session.
    - `get_time() -> str or None`: Retrieves the time recorded for the swimming result.

    Usage Example:
    ```python
    session_manager = SessionManager()
    result_instance = Result('result_id_here', session_manager, update_interval=120)
    result_time = result_instance.get_time()
    ```

    Details:
    - This class inherits from `ScraperMixin` to leverage common functionality for making HTTP requests.
    - `result_id` is required to identify the swimming result.
    - `sessionManager` is needed for making HTTP requests, and `update_interval` sets the minimum time between updates.
    - Use `get_time()` to retrieve the recorded time for the swimming result.
    - The time is returned as a string.
    - In case of an error or no data, None is returned.
    """
    # TODO: Add more methods to retrieve information about the result. (e.g. splits)

    def __init__(self, result_id, session, update_interval=60):
        """
        Initializes the Result with a result ID and a requests session.

        Parameters:
        - result_id (str): The ID of the result.
        - session (requests.Session): The requests session to be used for making HTTP requests.
        """
        super().__init__(session, update_interval)
        self.result_id = result_id

    def get_time(self):
        """
        Retrieves the time recorded for the swimming result.

        Returns:
        - str: The time recorded for the result.
        """
        params = {'page': 'resultDetail', 'id': self.result_id}
        try:
            soup = self._get_page_content(params)
            data = soup.find('td', {'class': 'swimtimeLarge'}).text
        except AttributeError:
            return None
        return data
