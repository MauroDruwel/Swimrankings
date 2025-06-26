"""
Mixin classes providing common functionality for scraper classes.
"""

import requests
import time
from bs4 import BeautifulSoup

from .constants import BASE_URL


class ScraperMixin:
    """
    A mixin class providing common functionality for other scraper classes.

    Attributes:
    - `sessionManager` (SessionManager): The SessionManager instance for making HTTP requests.
    - `page_content` (BeautifulSoup or None): The HTML content of the last fetched page, parsed with BeautifulSoup.
    - `update_interval` (int): The minimum time interval (in seconds) between consecutive updates.
    - `last_updated` (float): The timestamp of the last page update.

    Methods:
    - `__init__(sessionManager, update_interval=60, max_requests_per_minute=30)`: Initializes the ScraperMixin with a requests session.
    - `_update_page_content(params)`: Updates the page content with the HTML content of a page with the specified parameters.
    - `_get_page_content(params)`: Retrieves the HTML content of a page with the specified parameters.

    Usage Example:
    ```python
    session_manager = SessionManager()
    mixin_instance = ScraperMixin(session_manager, update_interval=120)
    params = {'param1': 'value1', 'param2': 'value2'}
    html_content = mixin_instance._get_page_content(params)
    ```

    Details:
    - This mixin class is designed to be used in conjunction with other scraper classes.
    - It provides a common set of methods for fetching and updating page content.
    - `sessionManager` is required for making HTTP requests, and `update_interval` sets the minimum time between updates.
    - Use `_get_page_content(params)` to retrieve HTML content, and `_update_page_content(params)` to force an update.
    - The page content is stored in the `page_content` attribute, parsed with BeautifulSoup.
    - Implement this mixin in other scraper classes to share common functionality.
    """
    
    def __init__(self, sessionManager, update_interval=60):
        """
        Initializes the ScraperMixin with a requests session.

        Parameters:
        - `sessionManager` (SessionManager): The requests session to be used for making HTTP requests.
        - `update_interval` (int): The minimum time interval (in seconds) between consecutive updates.
        """
        self.sessionManager = sessionManager
        self.last_request = None
        self.page_content = None
        self.update_interval = update_interval
        self.last_updated = None

    def _update_page_content(self, params):
        """
        Updates the page content with the HTML content of a page with the specified parameters.

        Parameters:
        - `params` (dict): The parameters to be included in the request.
        """
        try:
            self.sessionManager.check_request_rate_limit()
            page = self.sessionManager.get_session().get(BASE_URL, params=params)
            page.raise_for_status()  # Raise HTTPError for bad requests
            self.page_content = BeautifulSoup(page.content, "lxml")
            self.last_updated = time.time()
            self.sessionManager.add_request()
            if self.page_content.find('body') is None:
                raise requests.RequestException("Empty response")
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")

    def _get_page_content(self, params):
        """
        Retrieves the HTML content of a page with the specified parameters.

        Parameters:
        - `params` (dict): The parameters to be included in the request.

        Returns:
        - `str` or `None`: The HTML content of the page or `None` if an error occurs.
        """
        if self.last_updated is None or params != self.last_request or time.time() - self.last_updated > self.update_interval:
            self._update_page_content(params)
        self.last_request = params
        return self.page_content
