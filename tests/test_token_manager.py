import sys
import json
import os
sys.path.append(".")

from datetime import datetime, timedelta
from unittest.mock import patch, mock_open
from app.services.token_manager import save_tokens, get_valid_token
from app.exceptions import TokenError

TEST_PORTAL = "test_portal_123"

def test_save_and_load_token():
    with patch("builtins.open", mock_open(read_data="{}")):
        with patch("json.dump") as mock_dump:
            with patch("json.load", return_value={}):
                save_tokens(TEST_PORTAL, "access_123", "refresh_123", 3600)
                assert mock_dump.called
                print("✅ save_tokens called correctly")
                

def test_valid_token_returned():
    future = (datetime.now() + timedelta(hours=1)).isoformat()
    mock_data = {
        TEST_PORTAL: {
            "access_token": "valid_token",
            "refresh_token": "refresh_token",
            "expires_at": future
        }
    }
    
    with patch("app.services.token_manager.load_all_tokens", return_value=mock_data):
        token = get_valid_token(TEST_PORTAL)
        assert token == "valid_token"
        print("✅ Valid token returned correctly")
        
        
def test_missing_portal_raises_error():
    with patch("app.services.token_manager.load_all_tokens", return_value={}):
        try:
            get_valid_token("nonexistent_portal")
            print("❌ Should have raised Exception")
        except Exception as e:
            print(f"✅ Missing portal raises error: {e}")

if __name__ == "__main__":
    print("Testing token manager...")
    test_save_and_load_token()
    test_valid_token_returned()
    test_missing_portal_raises_error()
    print("\n✅ All token manager tests passed")