"""
Athlete class for retrieving athlete information and personal bests.
"""

import re
import unicodedata
from urllib.parse import urlparse, parse_qs

from .mixins import ScraperMixin
from .utils import convert_time


class Athlete(ScraperMixin):
    """
    Represents an athlete and provides methods to retrieve information about the athlete's personal bests and meets.

    Attributes:
    - `athlete_id` (str): The ID of the athlete.
    - `sessionManager` (SessionManager): The SessionManager instance for making HTTP requests.
    - `update_interval` (int): The minimum time interval (in seconds) between consecutive updates.

    Methods:
    - `__init__(athlete_id, sessionManager, update_interval=60)`: Initializes the Athlete with an athlete ID and a requests session.
    - `search_athletes(name, sessionManager, club_id=-1, gender=-1) -> list`: Static method to search for athletes by name.
    - `list_personal_bests() -> list`: Retrieves a list of personal bests for the athlete.
    - `list_meets() -> list`: Retrieves a list of meets in which the athlete has participated.

    Usage Example:
    ```python
    session_manager = SessionManager()
    
    # Search for athletes by name
    search_results = Athlete.search_athletes('Mauro Druwel', session_manager)
    if search_results:
        athlete_id = search_results[0]['athlete_id']
        athlete_instance = Athlete(athlete_id, session_manager, update_interval=120)
        personal_bests = athlete_instance.list_personal_bests()
        meets = athlete_instance.list_meets()
    
    # Or create directly with known ID
    athlete_instance = Athlete('athlete_id_here', session_manager, update_interval=120)
    personal_bests = athlete_instance.list_personal_bests()
    meets = athlete_instance.list_meets()
    ```

    Details:
    - This class inherits from `ScraperMixin` to leverage common functionality for making HTTP requests.
    - `athlete_id` is required to identify the athlete.
    - `sessionManager` is needed for making HTTP requests, and `update_interval` sets the minimum time between updates.
    - Use `search_athletes()` to find athletes by name, which returns a list of matching athletes with their details.
    - Use `list_personal_bests()` to retrieve a list of personal bests, represented as dictionaries.
    - The personal bests data includes event name, course length, time, result ID, and result URL.
    - In case of an error or no data, an empty list is returned.
    - Use `list_meets()` to retrieve a list of meets in which the athlete has participated.
    - The meets data includes meet ID, meet date, meet city, and meet name.
    - In case of an error or no data, an empty list is returned.
    """
    
    def __init__(self, athlete_id, sessionManager, update_interval=60):
        """
        Initializes the Athlete with an athlete ID and a requests session.

        Parameters:
        - `athlete_id` (str): The ID of the athlete.
        - `sessionManager` (SessionManager): The requests session to be used for making HTTP requests.
        - `update_interval` (int): The minimum time interval (in seconds) between consecutive updates.
        """
        super().__init__(sessionManager, update_interval)
        self.athlete_id = athlete_id

    @staticmethod
    def search_athletes(name, sessionManager, club_id=-1, gender=-1):
        """
        Searches for athletes by name.

        Parameters:
        - `name` (str): The name to search for (can be full name or last name).
        - `sessionManager` (SessionManager): The SessionManager instance for making HTTP requests.
        - `club_id` (int): Optional club ID filter (default: -1 for all clubs).
        - `gender` (int): Optional gender filter (default: -1 for all genders).

        Returns:
        - `list`: A list of dictionaries containing information about each matching athlete.
                  Each dictionary contains: athlete_id, name, birth_year, gender, country_code, club_name
        """
        # Create a temporary instance to use the mixin functionality
        temp_instance = Athlete("temp", sessionManager)
        
        params = {
            'internalRequest': 'athleteFind',
            'athlete_clubId': club_id,
            'athlete_gender': gender,
            'athlete_lastname': name,
            'athlete_firstname': ''
        }
        
        try:
            soup = temp_instance._get_page_content(params)
            table = soup.find('table', {'class': 'athleteSearch'})
            if not table:
                return []
        except AttributeError:
            return []

        data = []
        for row in table.find_all('tr', {'class': ['athleteSearch0', 'athleteSearch1']}):
            try:
                # Extract athlete name and ID
                name_cell = row.find('td', {'class': 'name'})
                if not name_cell:
                    continue
                    
                name_link = name_cell.find('a')
                if not name_link:
                    continue
                    
                athlete_name = name_link.get_text(strip=True).replace('<b>', '').replace('</b>', '')
                athlete_url = name_link['href']
                athlete_id = int(parse_qs(urlparse(athlete_url).query)['athleteId'][0])
                
                # Extract birth year
                date_cell = row.find('td', {'class': 'date'})
                birth_year = date_cell.get_text(strip=True) if date_cell else ''
                
                # Extract gender from image
                gender_img = row.find('img')
                gender = 'm' if gender_img and 'gender1.png' in gender_img['src'] else 'f'
                
                # Extract country code
                code_cell = row.find('td', {'class': 'code'})
                country_code = code_cell.get_text(strip=True) if code_cell else ''
                
                # Extract club name
                club_cell = row.find('td', {'class': 'club'})
                club_name = club_cell.get_text(strip=True) if club_cell else ''
                
                data.append({
                    'athlete_id': athlete_id,
                    'name': athlete_name,
                    'birth_year': birth_year,
                    'gender': gender,
                    'country_code': country_code,
                    'club_name': club_name
                })
                
            except (AttributeError, ValueError, KeyError, IndexError):
                # Skip rows that can't be parsed correctly
                continue
                
        return data

    def list_personal_bests(self, season="-1") -> list:
        """
        Retrieves a list of personal bests for the athlete.

        Returns:
        - `list`: A list of dictionaries containing information about each personal best.
        """
        params = {'page': 'athleteDetail', 'athleteId': self.athlete_id, 'pbest': season}
        try:
            soup = self._get_page_content(params)
            table = soup.find('table', {'class': 'athleteBest'})
        except AttributeError:
            return []

        data = []
        for row in table.find_all('tr', {'class': ['athleteBest0', 'athleteBest1']}):
            event_cell = row.find('td', {'class': 'event'})
            event_name = event_cell.find('a').get_text(strip=True)
            course_cell = row.find('td', {'class': 'course'})
            course_length = course_cell.get_text(strip=True)
            time_cell = row.find('td', {'class': ['time', 'swimtimeImportant']})
            time = convert_time(time_cell.get_text(strip=True))
            result_url = time_cell.find('a')['href']
            result_id = int(parse_qs(urlparse(result_url).query)['id'][0])
            fina_points = row.find('td', {'class': 'code'}).get_text(strip=True)
            data.append({'result_id': result_id, 'event_name': event_name, 'course_length': course_length, 'time': time, 'FINA Points': fina_points})
        return data

    def list_personal_details(self) -> list:
        """
        Retrieves personal details about the athlete.

        Returns:
        - `list`: A list containing information about the athlete.
        """
        params = {'page': 'athleteDetail', 'athleteId': self.athlete_id}
        try:
            soup = self._get_page_content(params)
            athlete_info = soup.find('div', {'id': 'athleteinfo'})
            name = athlete_info.find('div', {'id': 'name'})
            nation_club = athlete_info.find('div', {'id': 'nationclub'})

            personal_details = name.get_text(strip=True)
            gender_img = name.find('img')

            nation_specifics = nation_club.find('br').next_sibling.get_text(strip=True)
            club_name = nation_club.get_text(strip=True)[len(nation_specifics):]
        except AttributeError:
            return []

        data = []
        data.append({'first_name': re.sub(r'[0-9()]', '', personal_details.split(', ')[1])})
        data.append({'last_name': personal_details.split(',')[0]})
        data.append({'year_of_birth': re.sub(r'\D', '', personal_details)})
        data.append({'gender': f'{'m' if gender_img['src'] == 'images/gender1.png' else 'f'}'})
        data.append({'club_name': club_name})
        data.append({'country_name': nation_specifics[6:]})
        data.append({'country_code': nation_specifics[:3]})

        return data

    def list_meets(self) -> list:
        """
        Retrieves a list of meets in which the athlete has participated.

        Returns:
        - `list`: A list of dictionaries containing information about each meet.
        """
        params = {'page': 'athleteDetail', 'athleteId': self.athlete_id, 'athletePage': 'MEET'}
        try:
            soup = self._get_page_content(params)
            table = soup.find('table', {'class': 'athleteMeet'})
        except AttributeError:
            return []

        data = []
        for row in table.find_all('tr', {'class': ['athleteMeet0', 'athleteMeet1']}):
            date_cell = row.find('td', {'class': 'date'})
            meet_date = unicodedata.normalize("NFKD", date_cell.get_text(strip=True))
            city_cell = row.find('td', {'class': 'city'})
            meet_city = city_cell.find('a').get_text(strip=True)
            meet_name = city_cell.find('a')['title']
            meet_url = city_cell.find('a')['href']
            meet_id = int(parse_qs(urlparse(meet_url).query)['meetId'][0])
            data.append({'meet_id': meet_id, 'meet_date': meet_date, 'meet_city': meet_city, 'meet_name': meet_name})
        return data
