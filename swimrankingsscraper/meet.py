"""
Meet class for retrieving swimming meet information.
"""

import re
import unicodedata
from urllib.parse import urlparse, parse_qs

from .mixins import ScraperMixin


class Meet(ScraperMixin):
    """
    Represents a swimming meet and provides methods to retrieve information about clubs, events, and results.

    Attributes:
    - `meet_id` (str): The ID of the meet.
    - `sessionManager` (SessionManager): The SessionManager instance for making HTTP requests.
    - `update_interval` (int): The minimum time interval (in seconds) between consecutive updates.

    Methods:
    - `__init__(meet_id, sessionManager, update_interval=60)`: Initializes the Meet with a meet ID and a requests session.
    - `list_clubs() -> list`: Retrieves a list of clubs that participated in the meet.
    - `list_events() -> list`: Retrieves a list of events that took place in the meet.
    - `list_races(event_id, gender) -> list`: Retrieves a list of different races within the same event in the meet.
    - `list_results(event_id, gender, race_id) -> list`: Retrieves a list of results for a specific event in the meet.

    Usage Example:
    ```python
    session_manager = SessionManager()
    meet_instance = Meet('meet_id_here', session_manager, update_interval=120)
    clubs = meet_instance.list_clubs()
    events = meet_instance.list_events()
    races = meet_instance.list_races('event_id_here', 'gender_here')
    results = meet_instance.list_results('event_id_here', 'gender_here', race_id_here)
    ```

    Details:
    - This class inherits from `ScraperMixin` to leverage common functionality for making HTTP requests.
    - `meet_id` is required to identify the meet.
    - `sessionManager` is needed for making HTTP requests, and `update_interval` sets the minimum time between updates.
    - Use `list_clubs()` to retrieve a list of clubs that participated in the meet.
    - The clubs data includes club ID and club name.
    - In case of an error or no data, an empty list is returned.
    - Use `list_events()` to retrieve a list of events that took place in the meet.
    - The events data includes event ID, event gender, and event name.
    - In case of an error or no data, an empty list is returned.
    - Use `list_races(event_id, gender)` to retrieve a list of different races within the same event in the meet.
    - The races data includes race ID and race name.
    - In case of an error or no data, an empty list is returned.
    - Use `list_results(event_id, gender, race_id)` to retrieve a list of results for a specific event in the meet.
    - The results data includes result ID, athlete name, club name, swim time, and split times.
    - In case of an error or no data, an empty list is returned.
    """

    def __init__(self, meet_id, session, update_interval=60):
        """
        Initializes the Meet with a meet ID and a requests session.

        Parameters:
        - meet_id (str): The ID of the meet.
        - session (requests.Session): The requests session to be used for making HTTP requests.
        """
        super().__init__(session, update_interval)
        self.meet_id = meet_id

    def list_clubs(self):
        """
        Retrieves a list of clubs that participated in the meet.

        Returns:
        - list: A list of dictionaries containing information about each club.
        """
        params = {'page': 'meetDetail', 'meetId': self.meet_id}
        try:
            soup = self._get_page_content(params)
            table = soup.find('table', {'class': 'meetSearch'})
        except AttributeError:
            return []

        data = []
        for row in table.find_all('tr', {'class': ['meetResult0', 'meetResult1']}):
            club_cell = row.find('td', {'class': 'club'})
            club_url = club_cell.find('a')['href']
            club_id = parse_qs(urlparse(club_url).query)['clubId'][0]
            club_name = club_cell.find('a').get_text(strip=True)

            data.append({'club_id': club_id, 'club_name': club_name})

        return data

    def list_events(self):
        """
        Retrieves a list of events that took place in the meet.

        Returns:
        - list: A list of dictionaries containing information about each event.
        """
        params = {'page': 'meetDetail', 'meetId': self.meet_id}
        try:
            soup = self._get_page_content(params)
            table = soup.find('table', {'class': 'navigation'})
        except AttributeError:
            return []
        data = []
        # Add Men's events
        search_text = "Men's events: "
        menu = table.find(lambda tag: tag.name == 'td' and tag['class'][0] == 'navigation' and search_text in tag.text)
        for item in menu.find_all('option'):
            if item['value'] != "0":
                data.append({'event_id': item['value'], 'event_gender': '1', 'event_name': item.get_text(strip=True)})
        # Add Women's events
        search_text = "Women's events: "
        menu = table.find(lambda tag: tag.name == 'td' and tag['class'][0] == 'navigation' and search_text in tag.text)
        for item in menu.find_all('option'):
            if item['value'] != "0":
                data.append({'event_id': item['value'], 'event_gender': '2', 'event_name': item.get_text(strip=True)})
        return data

    def list_races(self, event_id, gender):
        """
        Retrieves a list of different races within the same event in the meet.

        Parameters:
        - event_id (str): The ID of the event.
        - gender (str): 1 for male, 2 for female.

        returns:
        - list: A list of dictionaries containing information about each race.
        """
        params = {'page': 'meetDetail', 'meetId': self.meet_id, 'gender': gender, 'styleId': event_id}
        try:
            soup = self._get_page_content(params)
            tables = soup.find_all('table', {'class': 'meetResult'})
        except AttributeError:
            return []
        races = []
        for (id, table) in enumerate(tables):
            head = table.find('tr', {'class': 'meetResultHead'})
            name_cell = head.find('th', {'class': 'event'})
            name = unicodedata.normalize("NFKD", name_cell.get_text(strip=True))
            races.append({'race_id': id+1, 'race_name': name})
        return races

    def list_results(self, event_id, gender, race_id):
        """
        Retrieves a list of results for a specific event in the meet.

        Parameters:
        - event_id (str): The ID of the event.
        - gender (str): 1 for male, 2 for female.
        - race_id (int): a number coronsponding with a specific race.

        Returns:
        - list: A list of dictionaries containing information about each result.
        """
        params = {'page': 'meetDetail', 'meetId': self.meet_id, 'gender': gender, 'styleId': event_id}
        try:
            soup = self._get_page_content(params)
            tables = soup.find_all('table', {'class': 'meetResult'})
        except AttributeError:
            return []
        results = []
        for row in tables[race_id-1].find_all('tr', {'class': ['meetResult0', 'meetResult1']}):
            name_cell = row.find('td', {'class': 'name'})
            name = name_cell.find('a').get_text(strip=True)
            name_url = name_cell.find('a')['href']
            athlete_id = parse_qs(urlparse(name_url).query)['athleteId'][0]
            club_cell = row.find_all('td', {'class': 'name'})[1]
            club_name = club_cell.find('a').get_text(strip=True)
            time_cell = row.find('td', {'class': 'swimtime'})
            time = time_cell.find('a').get_text(strip=True)
            try:
                split_times_rough = time_cell.find('a')['onmouseover']
            except KeyError:
                split_times_rough = ""
            pattern = r"<td class=\\'split1\\'>(.*?)<\/td>"
            split_times = re.findall(pattern, split_times_rough)
            result_url = time_cell.find('a')['href']
            result_id = parse_qs(urlparse(result_url).query)['id'][0]
            results.append({'result_id': result_id, 'athlete_id': athlete_id, 'name': name, 'club_name': club_name, 'time': time, 'split_times': split_times})
        return results
