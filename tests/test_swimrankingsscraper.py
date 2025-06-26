import unittest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
import time
import tests.values_for_testing as values_for_testing
from swimrankingsscraper import SwimrankingsScraper, Athlete, Meet, Result, Meets, Club
from swimrankingsscraper.mixins import ScraperMixin
from swimrankingsscraper.constants import BASE_URL

class TestSwimrankingsScraper(unittest.TestCase):

    def setUp(self):
        # Create a mock session manager for testing
        self.mock_session_manager = MagicMock()
        # Create an instance of the SwimScraper with the mock session manager
        self.scraper = SwimrankingsScraper()
        self.scraper.sessionManager = self.mock_session_manager

    def test_init(self):
        # Test that the scraper initializes properly 
        # (removing the url attribute test since it's no longer exposed)
        self.assertIsNotNone(self.scraper.sessionManager)
        self.assertEqual(self.scraper.sessionManager, self.mock_session_manager)

    def test_get_athlete(self):
        athlete_id = 123456
        athlete_instance = self.scraper.get_athlete(athlete_id)
        # Ensure that the Athlete instance is created with the correct parameters
        self.assertEqual(athlete_instance.athlete_id, athlete_id)
        self.assertEqual(athlete_instance.sessionManager, self.mock_session_manager)

    def test_get_meet(self):
        meet_id = 789012
        meet_instance = self.scraper.get_meet(meet_id)
        # Ensure that the Meet instance is created with the correct parameters
        self.assertEqual(meet_instance.meet_id, meet_id)
        self.assertEqual(meet_instance.sessionManager, self.mock_session_manager)

    def test_get_result(self):
        result_id = 345678
        results_instance = self.scraper.get_result(result_id)
        # Ensure that the Results instance is created with the correct parameters
        self.assertEqual(results_instance.result_id, result_id)
        self.assertEqual(results_instance.sessionManager, self.mock_session_manager)

    def test_get_meets(self):
        meets_instance = self.scraper.get_meets()
        # Ensure that the Meets instance is created with the correct parameters
        self.assertEqual(meets_instance.sessionManager, self.mock_session_manager)

    def test_get_club(self):
        club_id = 901234
        club_instance = self.scraper.get_club(club_id)
        # Ensure that the Club instance is created with the correct parameters
        self.assertEqual(club_instance.club_id, club_id)
        self.assertEqual(club_instance.sessionManager, self.mock_session_manager)

class TestScraperMixin(unittest.TestCase):
    def setUp(self):
        # Create a mock SessionManager for testing
        self.mock_session_manager = MagicMock()

        # Create an instance of ScraperMixin for testing
        self.scraper_mixin = ScraperMixin(self.mock_session_manager, update_interval=60)
    
    def test_init(self):
        self.assertEqual(self.scraper_mixin.sessionManager, self.mock_session_manager)
        self.assertEqual(self.scraper_mixin.update_interval, 60)
        self.assertEqual(self.scraper_mixin.last_updated, None)
        self.assertEqual(self.scraper_mixin.page_content, None)

    @patch('time.time')
    def test__update_page_content(self, mock_time):
        # Mock the time.time method to return a fixed time
        fixed_time = time.mktime(time.strptime('2018-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        mock_time.return_value = fixed_time

        # Mock the get_session method of SessionManager
        self.mock_session_manager.get_session.return_value.get.return_value.raise_for_status.side_effect = None

        # Mock the requests.get method to return a mock response
        mock_response = MagicMock()
        mock_response.content = b'<html><body>Hello, world!</body></html>'
        self.mock_session_manager.get_session.return_value.get.return_value = mock_response

        # Call the _update_page_content method with mock parameters
        self.scraper_mixin._update_page_content(params={'param1': 'value1', 'param2': 'value2'})

        # Assertions
        self.assertEqual(self.scraper_mixin.page_content, BeautifulSoup(b'<html><body>Hello, world!</body></html>', 'lxml'))
        self.assertEqual(self.scraper_mixin.last_updated, fixed_time)
        self.mock_session_manager.add_request.assert_called_once()

    @patch('time.time')
    def test__get_page_content_first_request(self, mock_time):
        # Mock the time.time method to return a fixed time
        fixed_time = time.mktime(time.strptime('2018-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        mock_time.return_value = fixed_time

        # Mock the _update_page_content method to avoid making actual requests
        self.scraper_mixin._update_page_content = MagicMock()

        # Call the _get_page_content method with mock parameters
        params = {'param1': 'value1', 'param2': 'value2'}
        result = self.scraper_mixin._get_page_content(params)

        # Assertions
        self.assertEqual(result, self.scraper_mixin.page_content)
        self.assertEqual(self.scraper_mixin.last_request, params)

        self.scraper_mixin._update_page_content.assert_called_once_with(params)
    
    @patch('time.time')
    def test__get_page_content_cash_hit(self, mock_time):
        # Mock the time.time method to return a fixed time
        fixed_time = time.mktime(time.strptime('2018-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        mock_time.return_value = fixed_time
        
        # Mock the requests.get method to return a mock response
        mock_response = MagicMock()
        mock_response.content = b'<html><body>Hello, world!</body></html>'
        self.mock_session_manager.get_session.return_value.get.return_value = mock_response

        # Call the _get_page_content method twice with the same mock parameters
        result1 = self.scraper_mixin._get_page_content({'param1': 'value1', 'param2': 'value2'})
        result2 = self.scraper_mixin._get_page_content({'param1': 'value1', 'param2': 'value2'})

        # Assertions
        self.assertEqual(result1, self.scraper_mixin.page_content)
        self.assertEqual(result2, self.scraper_mixin.page_content)
        self.mock_session_manager.get_session.return_value.get.assert_called_once()

    @patch('time.time')
    def test__get_page_content_cash_miss(self, mock_time):
        # Mock the time.time method to return a fixed time
        fixed_time = time.mktime(time.strptime('2018-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        mock_time.return_value = fixed_time
        
        # Mock the requests.get method to return a mock response
        mock_response = MagicMock()
        mock_response.content = b'<html><body>Hello, world!</body></html>'
        self.mock_session_manager.get_session.return_value.get.return_value = mock_response

        # Call the _get_page_content method twice with different mock parameters
        result1 = self.scraper_mixin._get_page_content({'param1': 'value1', 'param2': 'value2'})
        result2 = self.scraper_mixin._get_page_content({'param1': 'value1', 'param2': 'value3'})

        # Assertions
        self.assertEqual(result1, self.scraper_mixin.page_content)
        self.assertEqual(result2, self.scraper_mixin.page_content)
        self.assertEqual(self.mock_session_manager.get_session.return_value.get.call_count, 2)

    @patch('time.time')
    def test__get_page_content_update_interval(self, mock_time):
        # Mock the time.time method to return a fixed time
        fixed_time = time.mktime(time.strptime('2018-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        mock_time.return_value = fixed_time

        # Mock the requests.get method to return a mock response
        mock_response = MagicMock()
        mock_response.content = b'<html><body>Hello, world!</body></html>'
        self.mock_session_manager.get_session.return_value.get.return_value = mock_response

        # Call the _get_page_content method twice with same mock parameters but change the time in between
        result1 = self.scraper_mixin._get_page_content({'param1': 'value1', 'param2': 'value2'})
        mock_time.reset_mock()
        mock_time.return_value = fixed_time + 61
        result2 = self.scraper_mixin._get_page_content({'param1': 'value1', 'param2': 'value2'})

        # Assertions
        self.assertEqual(result1, self.scraper_mixin.page_content)
        self.assertEqual(result2, self.scraper_mixin.page_content)
        self.assertEqual(self.mock_session_manager.get_session.return_value.get.call_count, 2)


class TestAthlete(unittest.TestCase):

    def setUp(self):
        self.athete_id = 4787911
        self.mock_session_manager = MagicMock()
        self.athlete = Athlete(self.athete_id, self.mock_session_manager)

    def test_list_personal_bests_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.athlete._get_page_content = MagicMock()
        self.athlete._get_page_content.return_value = values_for_testing.athlete_detail_page
        # Call the list_personal_bests method
        self.personal_best = self.athlete.list_personal_bests()

        # Assertions 
        self.athlete._get_page_content.assert_called_once_with({'page': 'athleteDetail', 'athleteId': self.athete_id, 'pbest': '-1'})
        self.assertEqual(self.personal_best, values_for_testing.athlete_personal_best)

    def test_list_personal_bests_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.athlete._get_page_content = MagicMock()
        self.athlete._get_page_content.return_value = None
        # Call the list_personal_bests method
        self.personal_best = self.athlete.list_personal_bests()

        # Assertions 
        self.athlete._get_page_content.assert_called_once_with({'page': 'athleteDetail', 'athleteId': self.athete_id, 'pbest': '-1'})
        self.assertEqual(self.personal_best, [])

    def test_list_personal_bests_season_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.athlete._get_page_content = MagicMock()
        self.athlete._get_page_content.return_value = values_for_testing.athlete_detail_season_page
        # Call the list_personal_bests method
        self.personal_best = self.athlete.list_personal_bests(season='2024')

        # Assertions 
        self.athlete._get_page_content.assert_called_once_with({'page': 'athleteDetail', 'athleteId': self.athete_id, 'pbest': '2024'})
        self.assertEqual(self.personal_best, values_for_testing.athlete_season_best)

    def test_list_personal_details_success(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.athlete._get_page_content = MagicMock()
        self.athlete._get_page_content.return_value = values_for_testing.athlete_detail_page
        # Call the list_personal_details method
        self.personal_details = self.athlete.list_personal_details()

        #Assertions
        self.athlete._get_page_content.assert_called_once_with({'page': 'athleteDetail', 'athleteId': self.athete_id})
        self.assertEqual(self.personal_details, values_for_testing.athlete_personal_details)

    def test_list_personal_details_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.athlete._get_page_content = MagicMock()
        self.athlete._get_page_content.return_value = None
        # Call the list_personal_details method
        self.personal_details = self.athlete.list_personal_details()

        #Assertions
        self.athlete._get_page_content.assert_called_once_with({'page': 'athleteDetail', 'athleteId': self.athete_id})
        self.assertEqual(self.personal_details, [])

    def test_list_meets_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.athlete._get_page_content = MagicMock()
        self.athlete._get_page_content.return_value = values_for_testing.athlete_meets_page
        # Call the list_meets method
        self.meets = self.athlete.list_meets()

        # Assertions 
        self.athlete._get_page_content.assert_called_once_with({'page': 'athleteDetail', 'athleteId': self.athete_id, 'athletePage': 'MEET'})
        self.assertEqual(self.meets, values_for_testing.athlete_meets)

    def test_list_meets_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.athlete._get_page_content = MagicMock()
        self.athlete._get_page_content.return_value = None
        # Call the list_meets method
        self.meets = self.athlete.list_meets()

        # Assertions 
        self.athlete._get_page_content.assert_called_once_with({'page': 'athleteDetail', 'athleteId': self.athete_id, 'athletePage': 'MEET'})
        self.assertEqual(self.meets, [])

class TestMeet(unittest.TestCase):

    def setUp(self):
        self.meet_id = 642564
        self.gender = 1
        self.event_id = 1
        self.race_id = 1
        self.event_splits_id = 2
        self.mock_session_manager = MagicMock()
        self.meet = Meet(self.meet_id, self.mock_session_manager)

    def test_list_clubs_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meet._get_page_content = MagicMock()
        self.meet._get_page_content.return_value = values_for_testing.meet_detail_page
        # Call the list_clubs method
        self.clubs = self.meet.list_clubs()

        # Assertions 
        self.meet._get_page_content.assert_called_once_with({'page': 'meetDetail', 'meetId': self.meet_id})
        self.assertEqual(self.clubs, values_for_testing.meet_clubs)

    def test_list_clubs_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meet._get_page_content = MagicMock()
        self.meet._get_page_content.return_value = None
        # Call the list_clubs method
        self.clubs = self.meet.list_clubs()

        # Assertions 
        self.meet._get_page_content.assert_called_once_with({'page': 'meetDetail', 'meetId': self.meet_id})
        self.assertEqual(self.clubs, [])

    def test_list_events_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meet._get_page_content = MagicMock()
        self.meet._get_page_content.return_value = values_for_testing.meet_detail_page
        # Call the list_events method
        self.events = self.meet.list_events()

        # Assertions 
        self.meet._get_page_content.assert_called_once_with({'page': 'meetDetail', 'meetId': self.meet_id})
        self.assertEqual(self.events, values_for_testing.meet_events)

    def test_list_events_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meet._get_page_content = MagicMock()
        self.meet._get_page_content.return_value = None
        # Call the list_events method
        self.events = self.meet.list_events()

        # Assertions 
        self.meet._get_page_content.assert_called_once_with({'page': 'meetDetail', 'meetId': self.meet_id})
        self.assertEqual(self.events, [])

    def test_list_races_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meet._get_page_content = MagicMock()
        self.meet._get_page_content.return_value = values_for_testing.meet_races_page
        # Call the list_races method
        self.races = self.meet.list_races(self.event_id, self.gender)

        # Assertions
        self.meet._get_page_content.assert_called_once_with({'page': 'meetDetail', 'meetId': self.meet_id, 'gender': self.gender, 'styleId':self.event_id})
        self.assertEqual(self.races, values_for_testing.meet_races)

    def test_list_races_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meet._get_page_content = MagicMock()
        self.meet._get_page_content.return_value = None
        # Call the list_races method
        self.races = self.meet.list_races(self.event_id, self.gender)

        # Assertions
        self.meet._get_page_content.assert_called_once_with({'page': 'meetDetail', 'meetId': self.meet_id, 'gender': self.gender, 'styleId':self.event_id})
        self.assertEqual(self.races, [])

    def test_list_results_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meet._get_page_content = MagicMock()
        self.meet._get_page_content.return_value = values_for_testing.meet_races_page
        # Call the list_results method
        self.results = self.meet.list_results(self.event_id, self.gender, self.race_id)

        # Assertions
        self.meet._get_page_content.assert_called_once_with({'page': 'meetDetail', 'meetId': self.meet_id, 'gender': self.gender, 'styleId':self.event_id})
        self.assertEqual(self.results, values_for_testing.meet_results)

    def test_list_results_with_splits(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meet._get_page_content = MagicMock()
        self.meet._get_page_content.return_value = values_for_testing.meet_races_splits_page
        # Call the list_results method
        self.results = self.meet.list_results(self.event_splits_id, self.gender, self.race_id)

        # Assertions
        self.meet._get_page_content.assert_called_once_with({'page': 'meetDetail', 'meetId': self.meet_id, 'gender': self.gender, 'styleId':self.event_splits_id})
        self.assertEqual(self.results, values_for_testing.meet_results_splits)

    def test_list_results_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meet._get_page_content = MagicMock()
        self.meet._get_page_content.return_value = None
        # Call the list_races method
        self.races = self.meet.list_results(self.event_id, self.gender, self.race_id)

        # Assertions
        self.meet._get_page_content.assert_called_once_with({'page': 'meetDetail', 'meetId': self.meet_id, 'gender': self.gender, 'styleId':self.event_id})
        self.assertEqual(self.races, [])

class testResults(unittest.TestCase):
    def setUp(self):
        self.result_id = 1234567
        self.mock_session_manager = MagicMock()
        self.result = Result(self.result_id, self.mock_session_manager)

    def test_get_time_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.result._get_page_content = MagicMock()
        self.result._get_page_content.return_value = values_for_testing.result_detail_page
        # Call the list_results method
        self.results = self.result.get_time()
        # Assertions
        self.result._get_page_content.assert_called_once_with({'page': 'resultDetail', 'id': self.result_id})
        self.assertEqual(self.results, values_for_testing.result_time)

    def test_list_results_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.result._get_page_content = MagicMock()
        self.result._get_page_content.return_value = None
        # Call the list_results method
        self.results = self.result.get_time()

        # Assertions
        self.result._get_page_content.assert_called_once_with({'page': 'resultDetail', 'id': self.result_id})
        self.assertEqual(self.results, None)    

class TestMeets(unittest.TestCase):
    def setUp(self):
        self.mock_session_manager = MagicMock()
        self.meets = Meets(self.mock_session_manager)
        self.nation_id = 273
        self.time_period = '2024_m01'

    def test_list_time_periods_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meets._get_page_content = MagicMock()
        self.meets._get_page_content.return_value = values_for_testing.meets_page
        # Call the list_time_periods method
        self.time_periods = self.meets.list_time_periods()
        # Assertions
        self.meets._get_page_content.assert_called_once_with({'page': 'meetSelect', 'nationId': '0', 'selectPage': 'RECENT'})
        self.assertEqual(self.time_periods, values_for_testing.meets_time_periods)

    def test_list_time_periods_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meets._get_page_content = MagicMock()
        self.meets._get_page_content.return_value = None
        # Call the list_time_periods method
        self.time_periods = self.meets.list_time_periods()
        # Assertions
        self.meets._get_page_content.assert_called_once_with({'page': 'meetSelect', 'nationId': '0', 'selectPage': 'RECENT'})
        self.assertEqual(self.time_periods, [])
    
    def test_list_nations_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meets._get_page_content = MagicMock()
        self.meets._get_page_content.return_value = values_for_testing.meets_page
        # Call the list_time_periods method
        self.time_periods = self.meets.list_nations()
        # Assertions
        self.meets._get_page_content.assert_called_once_with({'page': 'meetSelect', 'nationId': '0', 'selectPage': 'RECENT'})
        self.assertEqual(self.time_periods, values_for_testing.meets_nations)
    
    def test_list_nations_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meets._get_page_content = MagicMock()
        self.meets._get_page_content.return_value = None
        # Call the list_time_periods method
        self.time_periods = self.meets.list_nations()
        # Assertions
        self.meets._get_page_content.assert_called_once_with({'page': 'meetSelect', 'nationId': '0', 'selectPage': 'RECENT'})
        self.assertEqual(self.time_periods, [])

    def test_list_meets_succes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meets._get_page_content = MagicMock()
        self.meets._get_page_content.return_value = values_for_testing.meets_page
        # Call the list_time_periods method
        self.time_periods = self.meets.list_meets(self.nation_id, self.time_period)
        # Assertions
        self.meets._get_page_content.assert_called_once_with({'page': 'meetSelect', 'nationId': self.nation_id, 'selectPage': self.time_period})
        self.assertEqual(self.time_periods, values_for_testing.meets_list)

    def test_list_meets_failure(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.meets._get_page_content = MagicMock()
        self.meets._get_page_content.return_value = None
        # Call the list_time_periods method
        self.time_periods = self.meets.list_meets(self.nation_id, self.time_period)
        # Assertions
        self.meets._get_page_content.assert_called_once_with({'page': 'meetSelect', 'nationId': self.nation_id, 'selectPage': self.time_period})
        self.assertEqual(self.time_periods, [])

class TestClub(unittest.TestCase):
    def setUp(self):
        self.club_id = 65929
        self.mock_session_manager = MagicMock()
        self.club = Club(self.club_id, self.mock_session_manager)
        self.athlete_gender = 0
        self.athlete_gender_parameter = 'CURRENT'

    def test_list_athletes(self):
        # Mock the _get_page_content method to avoid making actual requests
        self.club._get_page_content = MagicMock()
        self.club._get_page_content.return_value = values_for_testing.club_athlete_page
        # Call the list_athletes method
        self.athletes = self.club.list_athletes(self.athlete_gender)
        # Assertions
        self.club._get_page_content.assert_called_once_with({'page': 'rankingDetail', 'clubId': self.club_id, 'stroke': '9', 'athleteGender': self.athlete_gender_parameter})
        self.assertEqual(self.athletes, values_for_testing.club_athletes)

    def test_list_athletes_failure(self):
            # Mock the _get_page_content method to avoid making actual requests
        self.club._get_page_content = MagicMock()
        self.club._get_page_content.return_value = None
        # Call the list_athletes method
        self.athletes = self.club.list_athletes(self.athlete_gender)
        # Assertions
        self.club._get_page_content.assert_called_once_with({'page': 'rankingDetail', 'clubId': self.club_id, 'stroke': '9', 'athleteGender': self.athlete_gender_parameter})
        self.assertEqual(self.athletes, [])

if __name__ == '__main__':
    unittest.main()
