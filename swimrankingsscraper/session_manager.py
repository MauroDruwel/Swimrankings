"""
Session management for making HTTP requests with rate limiting.
"""

import requests
import time


class SessionManager:
    """
    Manages an HTTP session, tracks request history, and enforces request rate limits.

    Attributes:
    - `session`: An instance of `requests.Session` for making HTTP requests.
    - `request_history`: A list to track the timestamp of each request.
    - `last_updated`: Timestamp of the last request.
    - `max_requests_per_second`: Maximum allowed requests per second.
    - `max_per`: Timeframe in seconds within which the maximum requests are allowed.

    Methods:
    - `add_request()`: Adds a request timestamp to the request history.
    - `check_request_rate_limit()`: Checks and enforces the request rate limit.
    - `get_session()`: Retrieves the requests session.

    Usage Example:
    ```python
    manager = SessionManager()
    manager.add_request()
    manager.check_request_rate_limit()
    session = manager.get_session()
    ```

    Rate Limiting:
    - The rate limit is defined by `max_requests_per_second` within the timeframe of `max_per` seconds.
    - If the rate limit is reached, the function pauses execution to comply with the limit.

    Note:
    - Ensure to call `add_request()` before making each request.
    - Use `get_session()` to obtain the requests session for making HTTP requests.
    """
    
    def __init__(self, max_requests_per_timeframe=(15, 30)):
        self.session = requests.Session()
        self.request_history = []
        self.last_updated = None
        self.max_requests_per_second = max_requests_per_timeframe[0]
        self.max_per = max_requests_per_timeframe[1]

    def add_request(self):
        """
        Adds a request timestamp to the request history.
        """
        request_time = time.time()
        self.request_history.append(request_time)

    def check_request_rate_limit(self):
        """
        Checks and enforces the request rate limit.
        """
        current_time = time.time()
        window_start_time = current_time - self.max_per
        valid_requests = [t for t in self.request_history if t > window_start_time]

        if len(valid_requests) >= self.max_requests_per_second:
            time_to_wait = valid_requests[0] + self.max_per - current_time
            # print(f"Request rate limit reached. Waiting for {time_to_wait:.2f} seconds.")
            time.sleep(time_to_wait)
            self.request_history = [t for t in self.request_history if t > window_start_time + time_to_wait]

    def get_session(self):
        """
        Retrieves the requests session.

        Returns:
        - requests.Session: The requests session.
        """
        return self.session
