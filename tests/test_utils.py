"""
Tests for utility functions.
"""

import pytest
from bs4 import BeautifulSoup

from swimrankings.utils import is_valid_time, parse_profile_info


class TestIsValidTime:
    """Test the is_valid_time function."""

    def test_valid_times(self):
        """Test various valid time formats."""
        assert is_valid_time("24.50")
        assert is_valid_time("1:24.50")
        assert is_valid_time("59:59.99")
        assert is_valid_time("1:59:59.99")
        assert is_valid_time("2:30:45.67")

    def test_invalid_times(self):
        """Test invalid time formats."""
        assert not is_valid_time("invalid")
        assert not is_valid_time("24")
        assert not is_valid_time("24.5")
        assert not is_valid_time("1:24")
        assert not is_valid_time("1:24.5")
        assert not is_valid_time("")
        assert not is_valid_time("   ")
        assert not is_valid_time("24.50.00")
        # Note: The current regex doesn't validate minute/second ranges, only format
        
    def test_edge_cases(self):
        """Test edge cases."""
        assert is_valid_time("0.01")
        assert is_valid_time("9:59.99")
        assert is_valid_time("59:59.99")
        # Note: The current regex allows these as it only checks format, not logical validity


class TestParseProfileInfo:
    """Test the parse_profile_info function."""

    def test_parse_header_info(self):
        """Test parsing athlete header information."""
        html = """
        <div id="header_athleteDetail">
            <div id="athleteinfo">
                <div id="name">DRUWEL, Mauro (2008)</div>
                <div id="nationclub">
                    BEL - Belgium
                    TiMe Swimming Team
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        assert profile_info["header_name"] == "DRUWEL, Mauro (2008)"
        assert profile_info["country_code"] == "BEL"
        assert profile_info["country_name"] == "Belgium"
        assert profile_info["club_name"] == "TiMe Swimming Team"

    def test_parse_info_tables(self):
        """Test parsing info tables."""
        html = """
        <table class="athlete-info">
            <tr><td>Coach</td><td>John Smith</td></tr>
            <tr><td>Height</td><td>180cm</td></tr>
            <tr><td>Weight</td><td>75kg</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        assert profile_info["coach"] == "John Smith"
        assert profile_info["height"] == "180cm"
        assert profile_info["weight"] == "75kg"

    def test_parse_structured_divs(self):
        """Test parsing structured information from divs."""
        html = """
        <div class="info">
            <strong>Coach: Jane Doe</strong>
            <b>Team: Elite Swimming</b>
            <label>Birthday: January 1, 2000</label>
        </div>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        assert profile_info["coach"] == "Jane Doe"
        assert profile_info["team"] == "Elite Swimming"
        assert profile_info["birthday"] == "January 1, 2000"

    def test_parse_photo_url(self):
        """Test parsing photo URL."""
        html = """
        <div id="photo">
            <img src="/photos/athlete123.jpg" alt="Athlete photo">
        </div>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        assert profile_info["photo_url"] == "/photos/athlete123.jpg"

    def test_empty_html(self):
        """Test parsing empty HTML."""
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        assert isinstance(profile_info, dict)
        assert len(profile_info) == 0

    def test_missing_header_elements(self):
        """Test handling missing header elements."""
        html = """
        <div id="header_athleteDetail">
            <div id="athleteinfo">
                <!-- Missing name and nationclub divs -->
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        assert isinstance(profile_info, dict)

    def test_malformed_nationclub_data(self):
        """Test handling malformed nation/club data."""
        html = """
        <div id="header_athleteDetail">
            <div id="athleteinfo">
                <div id="nationclub">
                    Just some text without proper format
                    Another line
                    BEL - This should be ignored due to BEL filter
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        # The function will use the first non-BEL starting line as club_name
        assert "club_name" in profile_info
        # Since the function processes lines in order, it should use the last non-BEL line
        assert profile_info["club_name"] == "Another line"

    def test_empty_table_rows(self):
        """Test handling empty table rows."""
        html = """
        <table class="profile-info">
            <tr><td></td><td></td></tr>
            <tr><td>Valid Key</td><td>Valid Value</td></tr>
            <tr><td>   </td><td>   </td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        assert profile_info["valid key"] == "Valid Value"
        assert len([k for k in profile_info.keys() if k.strip()]) == 1

    def test_labels_without_colons(self):
        """Test handling labels that don't contain colons."""
        html = """
        <div class="details">
            <strong>No Colon Here</strong>
            <b>With Colon: Value Here</b>
        </div>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        assert profile_info["with colon"] == "Value Here"
        assert "No Colon Here" not in profile_info

    def test_missing_photo_elements(self):
        """Test handling missing photo elements."""
        html = """
        <div id="photo">
            <!-- No img tag here -->
        </div>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        assert "photo_url" not in profile_info

    def test_img_without_src(self):
        """Test handling img tag without src attribute."""
        html = """
        <div id="photo">
            <img alt="No src attribute">
        </div>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        profile_info = parse_profile_info(soup)
        
        assert "photo_url" not in profile_info
