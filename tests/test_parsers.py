"""
Tests for parsing functions.
"""

import pytest
from bs4 import BeautifulSoup

from swimrankings.parsers import parse_personal_bests, parse_athlete_best_table, parse_times_table
from swimrankings.models import PersonalBest


class TestParsePersonalBests:
    """Test the parse_personal_bests function."""

    def test_parse_athlete_best_table(self):
        """Test parsing athleteBest table."""
        html = """
        <table class="athleteBest">
            <tr><th>Event</th><th>Baan</th><th>Tijd</th><th>Rank</th><th>Datum</th><th>Plaats</th><th>Wedstrijd</th></tr>
            <tr>
                <td>50 Free</td>
                <td>25m</td>
                <td>24.50</td>
                <td>1</td>
                <td>2023-06-15</td>
                <td>Brussels</td>
                <td>Summer Championships</td>
            </tr>
            <tr>
                <td>100 Free</td>
                <td>50m</td>
                <td>53.20</td>
                <td>2</td>
                <td>2023-07-10</td>
                <td>Antwerp</td>
                <td>National Championships</td>
            </tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        personal_bests = parse_personal_bests(soup)
        
        assert len(personal_bests) == 2
        assert personal_bests[0].event == "50 Free"
        assert personal_bests[0].course == "SCM"  # 25m mapped to SCM
        assert personal_bests[0].time == "24.50"
        assert personal_bests[0].date == "2023-06-15"
        assert personal_bests[0].location == "Brussels"
        assert personal_bests[0].meet == "Summer Championships"

    def test_parse_fallback_tables(self):
        """Test parsing tables without athleteBest class."""
        html = """
        <table>
            <tr><th>Event</th><th>Time</th><th>Course</th><th>Date</th></tr>
            <tr><td>50 Back</td><td>29.50</td><td>LCM</td><td>2023-05-01</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        personal_bests = parse_personal_bests(soup)
        
        assert len(personal_bests) == 1
        assert personal_bests[0].event == "50 Back"
        assert personal_bests[0].time == "29.50"
        assert personal_bests[0].course == "LCM"

    def test_parse_no_tables(self):
        """Test parsing when no valid tables are found."""
        html = "<html><body><p>No tables here</p></body></html>"
        soup = BeautifulSoup(html, 'lxml')
        personal_bests = parse_personal_bests(soup)
        assert len(personal_bests) == 0

    def test_parse_tables_without_time_headers(self):
        """Test parsing tables that don't contain time-related headers."""
        html = """
        <table>
            <tr><th>Name</th><th>Country</th></tr>
            <tr><td>John Doe</td><td>USA</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, 'lxml')
        personal_bests = parse_personal_bests(soup)
        assert len(personal_bests) == 0


class TestParseAthleteBestTable:
    """Test the parse_athlete_best_table function."""

    def test_malformed_rows(self):
        """Test handling of rows with insufficient columns."""
        html = """
        <table class="athleteBest">
            <tr><th>Event</th><th>Baan</th><th>Tijd</th></tr>
            <tr><td>50 Free</td></tr>
            <tr><td>100 Free</td><td>25m</td><td>53.20</td><td>1</td><td>2023-07-10</td><td>Antwerp</td><td>National Championships</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table", class_="athleteBest")
        personal_bests = parse_athlete_best_table(table)
        
        # Should only parse the valid row
        assert len(personal_bests) == 1
        assert personal_bests[0].event == "100 Free"

    def test_invalid_times(self):
        """Test handling of invalid time values."""
        html = """
        <table class="athleteBest">
            <tr><th>Event</th><th>Baan</th><th>Tijd</th><th>Rank</th><th>Datum</th><th>Plaats</th><th>Wedstrijd</th></tr>
            <tr><td>50 Free</td><td>25m</td><td>DNF</td><td>-</td><td>2023-06-15</td><td>Brussels</td><td>Championships</td></tr>
            <tr><td>100 Free</td><td>25m</td><td>53.20</td><td>1</td><td>2023-07-10</td><td>Antwerp</td><td>Championships</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table", class_="athleteBest")
        personal_bests = parse_athlete_best_table(table)
        
        # Should only parse the row with valid time
        assert len(personal_bests) == 1
        assert personal_bests[0].time == "53.20"

    def test_empty_data_handling(self):
        """Test handling of empty or dash values."""
        html = """
        <table class="athleteBest">
            <tr><th>Event</th><th>Baan</th><th>Tijd</th><th>Rank</th><th>Datum</th><th>Plaats</th><th>Wedstrijd</th></tr>
            <tr><td>50 Free</td><td>25m</td><td>24.50</td><td>1</td><td>-</td><td>-</td><td>-</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table", class_="athleteBest")
        personal_bests = parse_athlete_best_table(table)
        
        assert len(personal_bests) == 1
        assert personal_bests[0].event == "50 Free"
        assert personal_bests[0].time == "24.50"
        assert personal_bests[0].date is None
        assert personal_bests[0].location is None
        assert personal_bests[0].meet is None


class TestParseTimesTable:
    """Test the parse_times_table function."""

    def test_no_header_row(self):
        """Test handling when table has no header row."""
        html = """
        <table>
            <tr><td>50 Free</td><td>24.50</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table")
        personal_bests = parse_times_table(table)
        
        # Should return empty list when no headers found
        assert len(personal_bests) == 0

    def test_missing_required_columns(self):
        """Test handling when essential columns are missing."""
        html = """
        <table>
            <tr><th>Name</th><th>Country</th></tr>
            <tr><td>John Doe</td><td>USA</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table")
        personal_bests = parse_times_table(table)
        
        assert len(personal_bests) == 0

    def test_insufficient_cells(self):
        """Test handling of rows with insufficient cells."""
        html = """
        <table>
            <tr><th>Event</th><th>Time</th></tr>
            <tr><td>50 Free</td></tr>
            <tr><td>100 Free</td><td>53.20</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table")
        personal_bests = parse_times_table(table)
        
        # Should only parse valid rows
        assert len(personal_bests) == 1
        assert personal_bests[0].event == "100 Free"

    def test_course_defaulting(self):
        """Test course defaulting to 'Unknown' when not provided."""
        html = """
        <table>
            <tr><th>Event</th><th>Time</th></tr>
            <tr><td>50 Free</td><td>24.50</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table")
        personal_bests = parse_times_table(table)
        
        assert len(personal_bests) == 1
        assert personal_bests[0].course == "Unknown"

    def test_various_header_names(self):
        """Test recognition of various header names."""
        html = """
        <table>
            <tr><th>Event</th><th>Time</th><th>Pool</th><th>Competition</th><th>Place</th></tr>
            <tr><td>50 Free</td><td>24.50</td><td>LCM</td><td>Olympics</td><td>Tokyo</td></tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table")
        personal_bests = parse_times_table(table)
        
        assert len(personal_bests) == 1
        assert personal_bests[0].course == "LCM"
        assert personal_bests[0].meet == "Olympics"
        assert personal_bests[0].location == "Tokyo"
