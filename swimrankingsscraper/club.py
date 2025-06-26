"""
Club class for retrieving swimming club information.
"""

from urllib.parse import urlparse, parse_qs

from .mixins import ScraperMixin


class Club(ScraperMixin):
    """
    Represents a club and provides methods to retrieve information about the club's athletes.

    Attributes:
    - `sessionManager` (SessionManager): The SessionManager instance for making HTTP requests.
    - `club_id` (str): The ID of the club.
    - `update_interval` (int): The minimum time interval (in seconds) between consecutive updates.

    Methods:
    - `__init__(sessionManager, club_id, update_interval=60)`: Initializes the Club with a requests session.
    - `list_athletes() -> List[Dict[str, Union[str, int]]]`: Retrieves a list of athletes in the club.

    Usage Example:
    ```python
    session_manager = SessionManager()
    club_instance = Club(session_manager, club_id='123456', update_interval=120)
    club_athletes = club_instance.list_athletes()
    ```

    Details:
    - This class inherits from `ScraperMixin` to leverage common functionality for making HTTP requests.
    - Use `list_athletes()` to retrieve a list of athletes in the club.
    - The returned data is in the form of a list of dictionaries, each containing information about an athlete.
    - Dictionary keys include 'athlete_id' and 'athlete_name'.
    - Athlete information is fetched based on the specified club and gender.
    """

    def __init__(self, club_id, session, update_interval=60):
        """
        Initializes the Ranking with a requests session.

        Parameters:
        - session (requests.Session): The requests session to be used for making HTTP requests.
        """
        super().__init__(session, update_interval)
        self.club_id = club_id

    def list_athletes(self, gender=0):
        """
        Retrieves a list of athletes.

        Parameters:
        - gender: 0 for ALL, 1 for Men, 2 for Women. Defaults to 0 this will only return currently active athletes.

        Returns:
        - list: A list of dictionaries containing information about each athlete.
        """
        athlete_gender = ['CURRENT', 'ALL_MEN', 'All_WOMEN'][gender]
        params = {'page': 'rankingDetail', 'clubId': self.club_id, 'stroke': '9', 'athleteGender': athlete_gender}
        try:
            soup = self._get_page_content(params)
            tables = soup.find_all('table', {'class': 'athleteList'})
        except AttributeError:
            return []
        athletes = []
        for table in tables:
            for row in table.find_all('tr', {'class': ['athleteSearch0', 'athleteSearch1']}):
                name_cell = row.find('td', {'class': 'name'})
                name = name_cell.find('a').get_text(strip=True)
                athlete_url = name_cell.find('a')['href']
                athlete_id = parse_qs(urlparse(athlete_url).query)['athleteId'][0]
                # TODO: Add more information about the athlete (Gender)
                athletes.append({'athlete_id': athlete_id, 'athlete_name': name})
        return athletes
