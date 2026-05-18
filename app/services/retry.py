import time
import httpx
from typing import Callable
from app.exceptions import RateLimitError
from app.logger import setup_logger

logger = setup_logger(__name__)

def with_retry(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
):
  """
    Execute a function with exponential backoff retry on rate limit errors.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for each subsequent delay
        
    Returns:
        Result of the function call
        
    Raises:
        RateLimitError: If max retries exceeded
        Exception: Any non-rate-limit exception
    """
  delay = initial_delay
  
  for attempt in range(1, max_retries + 1):
    try:
      return func()
    except RateLimitError as e:
      if attempt == max_retries:
        logger.error(f"Max retries reached for rate limit error: {e}")
        raise
      logger.warning(f"Rate limit hit — retrying in {delay:.1f}s (attempt {attempt}/{max_retries})")
      time.sleep(delay)
      delay *= backoff_factor
    except Exception as e:
      logger.error(f"Non-retryable error: {e}")
      raise
    
    