import httpx
from app.exceptions import HubSpotAPIError, RateLimitError
from app.logger import setup_logger

logger = setup_logger(__name__)

def handle_response(response: httpx.Response) -> dict:
    """
    Validate and parse HubSpot API response.
    Raises appropriate exceptions for error status codes.
    
    Args:
        response: httpx Response object
        
    Returns:
        Parsed JSON response dict
        
    Raises:
        RateLimitError: On 429 status
        HubSpotAPIError: On any other error status
    """
    if response.status_code == 429:
        logger.warning(f"HubSpot rate limit hit — status 429")
        raise RateLimitError(
            status_code=429,
            message="Rate limit exceeded",
        )
    
    if response.status_code >= 400:
        error_data = response.json()
        message = error_data.get("message", "Unknown error")
        correlation_id = error_data.get("correlationId")
        logger.error(f"HubSpot API error {response.status_code}: {message} — correlationId: {correlation_id}")
        raise HubSpotAPIError(
            status_code=response.status_code,
            message=message,
            correlation_id=correlation_id
        )
    
    logger.debug(f"HubSpot API response OK — status {response.status_code}")
    return response.json()