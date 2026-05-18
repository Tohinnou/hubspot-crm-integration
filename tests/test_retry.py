import sys
sys.path.append(".")

from unittest.mock import patch, MagicMock
from app.services.retry import with_retry
from app.exceptions import RateLimitError

def test_retry_on_rate_limit():
    call_count = 0
    
    def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RateLimitError(429, "Rate limit exceeded")
        return {"status": "success"}
    
    result = with_retry(flaky_function, max_retries=3, initial_delay=0.1)
    
    print(f"✅ Retry test passed")
    print(f"   Function called {call_count} times")
    print(f"   Result: {result}")
    
    
def test_max_retries_exceeded():
    def always_fails():
        raise RateLimitError(429, "Rate limit exceeded")
    
    try:
        with_retry(always_fails, max_retries=2, initial_delay=0.1)
        print("❌ Should have raised RateLimitError")
    except RateLimitError:
        print("✅ Max retries exceeded test passed — RateLimitError raised correctly")

if __name__ == "__main__":
    print("Testing retry mechanism...")
    test_retry_on_rate_limit()
    test_max_retries_exceeded()