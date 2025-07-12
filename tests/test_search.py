"""
Tests for search functionality.
"""

import pytest
from unittest.mock import Mock, patch

from swimrankings.search import Athletes
from swimrankings.exceptions import NetworkError, ParseError, AthleteNotFoundError


class TestAthletesParsing:
    """Test Athletes parsing functionality."""

    @patch('swimrankings.search.requests.get')
    def test_parse_error_handling(self, mock_get):
        """Test parse error handling in Athletes."""
        mock_response = Mock()
        mock_response.text = "<invalid>html"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock BeautifulSoup to raise an exception during parsing
        with patch('swimrankings.search.BeautifulSoup') as mock_soup:
            mock_soup.side_effect = Exception("Parse error")
            
            with pytest.raises(ParseError) as exc_info:
                Athletes(name="Test")
            
            assert "Failed to parse response" in str(exc_info.value)

    @patch('swimrankings.search.requests.get')
    def test_no_athletes_found_error(self, mock_get):
        """Test AthleteNotFoundError when no athletes are found."""
        # Mock HTML with no athlete results
        mock_html = '''
        <html>
            <body>
                <p>No results found</p>
            </body>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(AthleteNotFoundError) as exc_info:
            Athletes(name="NonexistentAthlete")
        
        assert "No athletes found for name 'NonexistentAthlete'" in str(exc_info.value)
        assert "with gender filter 'all'" in str(exc_info.value)

    @patch('swimrankings.search.requests.get')
    def test_no_athletes_found_with_gender_filter(self, mock_get):
        """Test AthleteNotFoundError with gender filter."""
        mock_html = '<html><body><p>No results</p></body></html>'
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(AthleteNotFoundError) as exc_info:
            Athletes(name="Test", gender="female")
        
        assert "with gender filter 'female'" in str(exc_info.value)

    @patch('swimrankings.search.requests.get')
    def test_advanced_filtering_edge_cases(self, mock_get):
        """Test advanced filtering with edge cases."""
        # Mock HTML with multiple athletes
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
            <tr class="athleteSearch0">
                <td class="name"><a href="?athleteId=3"><b>TEST, Three</b></a></td>
                <td class="date">1995</td>
                <td><img src="images/gender1.png"></td>
                <td class="code">CAN</td>
                <td class="club">Club C</td>
            </tr>
        </table>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        athletes = Athletes(name="Test")
        
        # Test filter_by_birth_year with no matches
        no_matches = athletes.filter_by_birth_year(2010, 2020)
        assert len(no_matches) == 0
        
        # Test filter_by_birth_year with single year range
        single_year = athletes.filter_by_birth_year(2000, 2000)
        assert len(single_year) == 1
        assert single_year[0].birth_year == 2000
        
        # Test filter_by_country with non-existent country
        no_country = athletes.filter_by_country("XYZ")
        assert len(no_country) == 0
        
        # Test filter_by_gender with no matches
        no_gender = athletes.filter_by_gender("unknown")
        assert len(no_gender) == 0

    @patch('swimrankings.search.requests.get')
    def test_athletes_object_creation(self, mock_get):
        """Test Athletes object creation and basic functionality."""
        mock_html = '''
        <table class="athleteSearch">
            <tr class="athleteSearch0">
                <td class="name"><a href="?athleteId=1"><b>TEST, One</b></a></td>
                <td class="date">2000</td>
                <td><img src="images/gender1.png"></td>
                <td class="code">USA</td>
                <td class="club">Club A</td>
            </tr>
        </table>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        athletes = Athletes(name="Test")
        
        # Test basic functionality
        assert len(athletes) == 1
        assert bool(athletes) == True
        assert athletes[0].full_name == "TEST, One"
        
        # Test iteration
        for athlete in athletes:
            assert athlete.full_name == "TEST, One"

    @patch('swimrankings.search.requests.get')
    def test_to_dict_with_empty_list(self, mock_get):
        """Test to_dict method with empty athlete list."""
        mock_html = '''
        <table class="athleteSearch">
            <tr class="athleteSearchHead"><th>Header</th></tr>
        </table>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Since no athletes found, this should raise AthleteNotFoundError
        with pytest.raises(AthleteNotFoundError):
            Athletes(name="Test")

    @patch('swimrankings.search.requests.get')
    def test_different_gender_parameter_values(self, mock_get):
        """Test different gender parameter values in search."""
        mock_html = '''
        <table class="athleteSearch">
            <tr class="athleteSearch0">
                <td class="name"><a href="?athleteId=1"><b>TEST, One</b></a></td>
                <td class="date">2000</td>
                <td><img src="images/gender1.png"></td>
                <td class="code">USA</td>
                <td class="club">Club A</td>
            </tr>
        </table>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test with different gender values
        for gender in ["all", "male", "female"]:
            athletes = Athletes(name="Test", gender=gender)
            assert len(athletes) == 1
            
            # Verify the correct gender parameter was sent in the request
            mock_get.assert_called()
            call_args = mock_get.call_args
            params = call_args[1]['params']
            assert params['athlete_gender'] == Athletes.GENDER_MAP[gender]
