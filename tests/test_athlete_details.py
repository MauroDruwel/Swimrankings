"""
Tests for athlete details functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from swimrankings import Athlete, PersonalBest, AthleteDetails
from swimrankings.exceptions import NetworkError, ParseError


class TestPersonalBest:
    """Test PersonalBest dataclass."""

    def test_personal_best_creation(self):
        """Test creating a PersonalBest instance."""
        pb = PersonalBest(
            event="50 Free",
            course="SCM",
            time="24.50",
            date="2023-06-15",
            meet="Summer Championships",
            location="Brussels"
        )
        
        assert pb.event == "50 Free"
        assert pb.course == "SCM"
        assert pb.time == "24.50"
        assert pb.date == "2023-06-15"
        assert pb.meet == "Summer Championships"
        assert pb.location == "Brussels"

    def test_personal_best_optional_fields(self):
        """Test PersonalBest with only required fields."""
        pb = PersonalBest(
            event="100 Back",
            course="LCM",
            time="1:02.45"
        )
        
        assert pb.event == "100 Back"
        assert pb.course == "LCM"
        assert pb.time == "1:02.45"
        assert pb.date is None
        assert pb.meet is None
        assert pb.location is None


class TestAthleteDetails:
    """Test AthleteDetails dataclass."""

    def test_athlete_details_creation(self):
        """Test creating an AthleteDetails instance."""
        pb1 = PersonalBest("50 Free", "SCM", "24.50")
        pb2 = PersonalBest("100 Free", "SCM", "53.20")
        
        details = AthleteDetails(
            athlete_id=12345,
            personal_bests=[pb1, pb2],
            profile_info={"coach": "John Doe", "team": "Swimming Club"},
            last_updated=datetime(2023, 6, 15, 10, 30)
        )
        
        assert details.athlete_id == 12345
        assert len(details.personal_bests) == 2
        assert details.personal_bests[0].event == "50 Free"
        assert details.profile_info["coach"] == "John Doe"
        assert details.last_updated.year == 2023


class TestAthleteDetailsMethod:
    """Test the get_details method on Athlete class."""

    @pytest.fixture
    def athlete(self):
        """Create a test athlete."""
        return Athlete(
            athlete_id=12345,
            full_name="Doe, John",
            birth_year=1995,
            gender="male",
            country="USA",
            club="Test Club",
            profile_url="https://www.swimrankings.net/index.php?page=athleteDetail&athleteId=12345"
        )

    def test_is_valid_time(self, athlete):
        """Test time validation method."""
        # Valid times
        assert athlete._is_valid_time("24.50")
        assert athlete._is_valid_time("1:24.50")
        assert athlete._is_valid_time("2:24:50.00")
        
        # Invalid times
        assert not athlete._is_valid_time("invalid")
        assert not athlete._is_valid_time("24")
        assert not athlete._is_valid_time("24.5")

    @patch('swimrankings.athlete.requests.get')
    def test_get_details_success(self, mock_get, athlete):
        """Test successful athlete details retrieval."""
        # Mock HTML response
        mock_html = """
        <html>
            <body>
                <table>
                    <tr><th>Event</th><th>Time</th><th>Course</th></tr>
                    <tr><td>50 Free</td><td>24.50</td><td>SCM</td></tr>
                    <tr><td>100 Free</td><td>53.20</td><td>SCM</td></tr>
                </table>
                <div class="info">
                    <strong>Coach:</strong> John Smith
                </div>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        details = athlete.get_details()
        
        assert isinstance(details, AthleteDetails)
        assert details.athlete_id == 12345
        assert isinstance(details.last_updated, datetime)
        
        # Check that the request was made correctly
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == athlete.profile_url
        assert kwargs['timeout'] == 30

    @patch('swimrankings.athlete.requests.get')
    def test_get_details_network_error(self, mock_get, athlete):
        """Test network error handling."""
        from requests.exceptions import RequestException
        
        mock_get.side_effect = RequestException("Connection failed")
        
        with pytest.raises(NetworkError) as exc_info:
            athlete.get_details()
        
        assert "Failed to fetch athlete details" in str(exc_info.value)

    @patch('swimrankings.athlete.requests.get')
    def test_get_details_parse_error(self, mock_get, athlete):
        """Test parse error handling."""
        mock_response = Mock()
        mock_response.text = "<invalid>html"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock BeautifulSoup to raise an exception during parsing
        with patch('swimrankings.athlete.BeautifulSoup') as mock_soup:
            mock_soup.side_effect = Exception("Parse error")
            
            with pytest.raises(ParseError):
                athlete.get_details()

    def test_parse_times_table_basic(self, athlete):
        """Test parsing a basic times table."""
        from bs4 import BeautifulSoup
        
        html = """
        <table>
            <tr><th>Event</th><th>Time</th><th>Course</th></tr>
            <tr><td>50 Free</td><td>24.50</td><td>SCM</td></tr>
            <tr><td>100 Free</td><td>53.20</td><td>LCM</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table')
        
        personal_bests = athlete._parse_times_table(table)
        
        assert len(personal_bests) == 2
        assert personal_bests[0].event == "50 Free"
        assert personal_bests[0].time == "24.50"
        assert personal_bests[0].course == "SCM"
        assert personal_bests[1].event == "100 Free"
        assert personal_bests[1].time == "53.20"
        assert personal_bests[1].course == "LCM"

    def test_parse_times_table_no_headers(self, athlete):
        """Test parsing a table without proper headers."""
        from bs4 import BeautifulSoup
        
        html = """
        <table>
            <tr><td>Some</td><td>Data</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table')
        
        personal_bests = athlete._parse_times_table(table)
        
        assert len(personal_bests) == 0

    def test_parse_profile_info(self, athlete):
        """Test parsing profile information."""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <body>
                <table class="athlete-info">
                    <tr><td>Coach</td><td>John Smith</td></tr>
                    <tr><td>Team</td><td>Swimming Club</td></tr>
                </table>
                <div class="details">
                    <strong>Height:</strong> 180cm
                    <b>Weight:</b> 75kg
                </div>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = athlete._parse_profile_info(soup)
        
        # Should extract some information, exact structure depends on implementation
        assert isinstance(profile_info, dict)

    def test_custom_timeout(self, athlete):
        """Test custom timeout parameter."""
        with patch('swimrankings.athlete.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html></html>"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            athlete.get_details(timeout=60)
            
            args, kwargs = mock_get.call_args
            assert kwargs['timeout'] == 60
