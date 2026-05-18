class HubSpotAPIError(Exception):
    """Raised when HubSpot API returns an error response."""
    
    def __init__(self, status_code: int, message: str, correlation_id: str = None):
        self.status_code = status_code
        self.message = message
        self.correlation_id = correlation_id
        super().__init__(f"HubSpot API Error {status_code}: {message}")

class TokenError(Exception):
    """Raised when token operations fail."""
    pass

class RateLimitError(HubSpotAPIError):
    """Raised when HubSpot rate limit is hit (429)."""
    pass