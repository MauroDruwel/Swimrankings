"""
Meets class for retrieving information about multiple swimming meets.
"""

import unicodedata
from urllib.parse import urlparse, parse_qs

from .mixins import ScraperMixin


class Meets(ScraperMixin):
    """
    Represents a list of meets and provides methods to retrieve information about the meets.

    Attributes:
    - `sessionManager` (SessionManager): The SessionManager instance for making HTTP requests.
    - `update_interval` (int): The minimum time interval (in seconds) between consecutive updates.

    Methods:
    - `__init__(sessionManager, update_interval=60)`: Initializes the Meets with a requests session.
    - `list_periods() -> List[Dict[str, Union[str, int]]]`: Retrieves a list of periods.
    - `list_nations() -> List[Dict[str, Union[str, int]]]`: Retrieves a list of nations.
    - `list_meets(nation_id=None, period_id='RECENT') -> List[Dict[str, Union[str, int]]]`: Retrieves a list of meets.

    Usage Example:
    ```python
    session_manager = SessionManager()
    meets_instance = Meets(session_manager, update_interval=120)
    recent_meets = meets_instance.list_meets(period_id='RECENT')
    ```

    Details:
    - This class inherits from `ScraperMixin` to leverage common functionality for making HTTP requests.
    - Use `list_periods()` to retrieve a list of periods.
    - Use `list_nations()` to retrieve a list of nations.
    - Use `list_meets()` to retrieve a list of meets, with optional filtering by nation and period.
    - The returned data is in the form of a list of dictionaries, each containing information about a meet.
    - Dictionary keys include 'meet_id', 'meet_date', 'meet_city', 'meet_name', and 'course_length'.
    - 'nation_id' and 'period_id' parameters in `list_meets()` allow optional filtering by nation and period, respectively.
    """

    def __init__(self, session, update_interval=60):
        """
        Initializes the Meets with a requests session.

        Parameters:
        - session (requests.Session): The requests session to be used for making HTTP requests.
        """
        super().__init__(session, update_interval)

    def list_time_periods(self):
        """
        Retrieves a list of periods.

        Returns:
        - list: A list of dictionaries containing information about each time period.
        """
        params = {'page': 'meetSelect', 'nationId': '0', 'selectPage': 'RECENT'}
        try:
            soup = self._get_page_content(params)
            menu = soup.find('select', {'name': 'selectPage'})
        except AttributeError:
            return []
        periods = []
        for item in menu.find_all('option'):
            if item['value'] != "RECENT" and item['value'] != "BYTYPE":
                periods.append({'period_id': item['value'], 'period_name': unicodedata.normalize("NFKD", item.get_text(strip=True))})
        return periods

    def list_nations(self):
        """
        Retrieves a list of nations.

        Returns:
        - list: A list of dictionaries containing information about each nation.
        """
        params = {'page': 'meetSelect', 'nationId': '0', 'selectPage': 'RECENT'}
        try:
            soup = self._get_page_content(params)
            menu = soup.find('select', {'name': 'nationId'})
        except AttributeError:
            return []
        nations = []
        for item in menu.find_all('option'):
            if item['value'] != "$$$":
                nations.append({'nation_id': item['value'], 'nation_name': unicodedata.normalize("NFKD", item.get_text(strip=True))})
        return nations

    def list_meets(self, nation_id=None, time_period_id='RECENT'):
        """
        Retrieves a list of meets.

        Parameters:
        - nation_id (str): The ID of the nation. Defaults to None.
        - time_period_id (str): The ID of the time period. Defaults to 'RECENT'.

        Returns:
        - list: A list of dictionaries containing information about each meet.
        """
        params = {'page': 'meetSelect', 'nationId': nation_id, 'selectPage': time_period_id}
        try:
            soup = self._get_page_content(params)
            tables = soup.find_all('table', {'class': 'meetSearch'})
        except AttributeError:
            return []
        meets = []
        for table in tables:
            for row in table.find_all('tr', {'class': ['meetSearch0', 'meetSearch1']}):
                date_cell = row.find('td', {'class': 'date'})
                meet_date = unicodedata.normalize("NFKD", date_cell.get_text(strip=True))
                city_cell = row.find('td', {'class': 'city'})
                meet_city = unicodedata.normalize("NFKD", city_cell.find('a').get_text(strip=True))
                meet_url = city_cell.find('a')['href']
                meet_name = row.find_all('td', {'class': 'name'})[1].find('a').get_text(strip=True)
                course_cell = row.find('td', {'class': 'course'})
                course_length = course_cell.get_text(strip=True)
                meet_id = parse_qs(urlparse(meet_url).query)['meetId'][0]
                meets.append({'meet_id': meet_id, 'meet_date': meet_date, 'meet_city': meet_city, 'meet_name': meet_name, 'course_length': course_length})
        return meets
