"""
Tests for the SwimRankings library.
"""

import pytest
from unittest.mock import Mock, patch

from swimrankings import Athletes, Athlete
from swimrankings.exceptions import (
    AthleteNotFoundError,
    InvalidGenderError,
    NetworkError,
)


class TestAthlete:
    """Test cases for the Athlete class."""
    
    def test_athlete_creation(self):
        """Test creating an Athlete instance."""
        athlete = Athlete(
            athlete_id=5199475,
            full_name="DRUWEL, Mauro",
            birth_year=2008,
            gender="male",
            country="BEL",
            club="BEL - TiMe Swimming Team",
            profile_url="https://www.swimrankings.net/index.php?page=athleteDetail&athleteId=5199475"
        )
        
        assert athlete.athlete_id == 5199475
        assert athlete.full_name == "DRUWEL, Mauro"
        assert athlete.first_name == "Mauro"
        assert athlete.last_name == "DRUWEL"
        assert athlete.birth_year == 2008
        assert athlete.gender == "male"
        assert athlete.country == "BEL"
        assert athlete.club == "BEL - TiMe Swimming Team"
        
    def test_athlete_string_representation(self):
        """Test string representation of Athlete."""
        athlete = Athlete(
            athlete_id=5199475,
            full_name="DRUWEL, Mauro",
            birth_year=2008,
            gender="male",
            country="BEL",
            club="BEL - TiMe Swimming Team",
            profile_url="https://example.com"
        )
        
        expected_str = "DRUWEL, Mauro (2008) - BEL"
        assert str(athlete) == expected_str
        
    def test_athlete_equality(self):
        """Test athlete equality based on ID."""
        athlete1 = Athlete(1, "Test, One", 2000, "male", "USA", "Club A", "url1")
        athlete2 = Athlete(1, "Test, Two", 2001, "female", "CAN", "Club B", "url2")
        athlete3 = Athlete(2, "Test, One", 2000, "male", "USA", "Club A", "url1")
        
        assert athlete1 == athlete2  # Same ID
        assert athlete1 != athlete3  # Different ID
        
    def test_name_parsing(self):
        """Test first and last name extraction."""
        athlete = Athlete(1, "SMITH, John", 2000, "male", "USA", "Club", "url")
        assert athlete.first_name == "John"
        assert athlete.last_name == "SMITH"
        
        # Test case where there's no comma
        athlete2 = Athlete(2, "Madonna", 2000, "female", "ITA", "Club", "url")
        assert athlete2.first_name == ""
        assert athlete2.last_name == "Madonna"
        
    def test_athlete_repr(self):
        """Test detailed string representation of Athlete."""
        athlete = Athlete(
            athlete_id=5199475,
            full_name="DRUWEL, Mauro",
            birth_year=2008,
            gender="male",
            country="BEL",
            club="BEL - TiMe Swimming Team",
            profile_url="https://example.com"
        )
        
        repr_str = repr(athlete)
        assert "Athlete(id=5199475" in repr_str
        assert "name='DRUWEL, Mauro'" in repr_str
        assert "birth_year=2008" in repr_str
        assert "gender='male'" in repr_str
        assert "country='BEL'" in repr_str
        assert "club='BEL - TiMe Swimming Team'" in repr_str
        
    def test_athlete_hash(self):
        """Test athlete hash based on ID."""
        athlete1 = Athlete(1, "Test, One", 2000, "male", "USA", "Club A", "url1")
        athlete2 = Athlete(1, "Test, Two", 2001, "female", "CAN", "Club B", "url2")
        athlete3 = Athlete(2, "Test, One", 2000, "male", "USA", "Club A", "url1")
        
        # Same ID should have same hash
        assert hash(athlete1) == hash(athlete2)
        # Different ID should have different hash
        assert hash(athlete1) != hash(athlete3)
        
        # Test that athletes can be used in sets
        athlete_set = {athlete1, athlete2, athlete3}
        assert len(athlete_set) == 2  # athlete1 and athlete2 are considered same due to same ID


class TestAthletes:
    """Test cases for the Athletes class."""
    
    def test_invalid_gender(self):
        """Test that invalid gender raises an exception."""
        with pytest.raises(InvalidGenderError):
            Athletes(name="Test", gender="invalid")
            
    @patch('swimrankings.athletes.requests.get')
    def test_network_error(self, mock_get):
        """Test that network errors are handled properly."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with pytest.raises(NetworkError):
            Athletes(name="Test")
            
    @patch('swimrankings.athletes.requests.get')
    def test_no_athletes_found(self, mock_get):
        """Test behavior when no athletes are found."""
        mock_response = Mock()
        mock_response.text = "<html><body>No results</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(AthleteNotFoundError):
            Athletes(name="NonexistentName")
            
    @patch('swimrankings.athletes.requests.get')
    def test_successful_search(self, mock_get):
        """Test successful athlete search."""
        # Mock HTML response similar to the real one
        mock_html = '''
        <table class="athleteSearch">
            <tr class="athleteSearchHead"><th>Header</th></tr>
            <tr class="athleteSearch0">
                <td width="8"></td>
                <td class="name">
                    <a href="?page=athleteDetail&amp;athleteId=5199475">
                        <b>DRUWEL, Mauro</b>
                    </a>
                </td>
                <td class="date">2008</td>
                <td><img src="images/gender1.png"></td>
                <td class="code">BEL</td>
                <td class="club">BEL - TiMe Swimming Team</td>
            </tr>
        </table>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        athletes = Athletes(name="Druwel")
        
        assert len(athletes) == 1
        athlete = athletes[0]
        assert athlete.athlete_id == 5199475
        assert athlete.full_name == "DRUWEL, Mauro"
        assert athlete.birth_year == 2008
        assert athlete.gender == "male"
        assert athlete.country == "BEL"
        assert athlete.club == "BEL - TiMe Swimming Team"
        
    def test_gender_mapping(self):
        """Test that gender values are mapped correctly."""
        assert Athletes.GENDER_MAP["all"] == -1
        assert Athletes.GENDER_MAP["male"] == 1
        assert Athletes.GENDER_MAP["female"] == 2
        
    @patch('swimrankings.athletes.requests.get')
    def test_filtering_methods(self, mock_get):
        """Test athlete filtering methods."""
        # Create mock athletes
        mock_html = '''
        <table class="athleteSearch">
            <tr class="athleteSearch0">
                <td class="name"><a href="?athleteId=1"><b>TEST, One</b></a></td>
                <td class="date">2000</td>
                <td><img src="images/gender1.png"></td>
                <td class="code">USA</td>
                <td class="club">Club A</td>
            </tr>
            <tr class="athleteSearch1">
                <td class="name"><a href="?athleteId=2"><b>TEST, Two</b></a></td>
                <td class="date">2005</td>
                <td><img src="images/gender2.png"></td>
                <td class="code">BEL</td>
                <td class="club">Club B</td>
            </tr>
        </table>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        athletes = Athletes(name="Test")
        
        # Test country filtering
        usa_athletes = athletes.filter_by_country("USA")
        assert len(usa_athletes) == 1
        assert usa_athletes[0].country == "USA"
        
        # Test birth year filtering
        young_athletes = athletes.filter_by_birth_year(2004, 2010)
        assert len(young_athletes) == 1
        assert young_athletes[0].birth_year == 2005
        
        # Test gender filtering
        male_athletes = athletes.filter_by_gender("male")
        assert len(male_athletes) == 1
        assert male_athletes[0].gender == "male"
        
        # Test to_dict method
        athletes_dict = athletes.to_dict()
        assert len(athletes_dict) == 2
        assert all(isinstance(item, dict) for item in athletes_dict)
