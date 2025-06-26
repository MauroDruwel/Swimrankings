"""
Utility functions for the SwimrankingsScraper package.
"""

from datetime import datetime


def convert_time(time_str):
    """
    Converts a time string to seconds.
    
    Args:
        time_str (str): Time string in format like "1:23.45" or "23.45"
        
    Returns:
        float: Time in seconds
    """
    # Remove trailing 'M' if it exists
    if time_str[-1] == 'M':
        time_str = time_str[:-1]

    # Parse the time string using datetime
    col_count = time_str.count(':')
    if col_count == 2:
        time_format = '%H:%M:%S.%f'
    elif col_count == 1:
        time_format = '%M:%S.%f'
    else:
        time_format = '%S.%f'
    time = datetime.strptime(time_str, time_format).time()
    total_second = time.second + time.minute * 60 + time.hour * 3600 + time.microsecond / 1000000
    return total_second
