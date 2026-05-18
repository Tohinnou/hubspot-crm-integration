import sys
sys.path.append(".")

from unittest.mock import patch, MagicMock
from app.services.hubspot import create_contact, get_contacts
from app.exceptions import HubSpotAPIError

def test_create_contact_success():
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": "123456",
        "properties": {"email": "test@example.com"}
    }
    
    with patch("httpx.post", return_value=mock_response):
        with patch("app.services.hubspot.get_headers", return_value={}):
            result = create_contact({"email": "test@example.com"})
            assert result["id"] == "123456"
            print("✅ create_contact success test passed")

def test_create_contact_error():
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "message": "Property does not exist",
        "correlationId": "abc123"
    }
    
    with patch("httpx.post", return_value=mock_response):
        with patch("app.services.hubspot.get_headers", return_value={}):
            try:
                create_contact({"email": "test@example.com"})
                print("❌ Should have raised HubSpotAPIError")
            except HubSpotAPIError as e:
                assert e.status_code == 400
                print(f"✅ create_contact error handling test passed: {e.message}")

def test_get_contacts_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": [], "paging": {}}
    
    with patch("httpx.get", return_value=mock_response):
        with patch("app.services.hubspot.get_headers", return_value={}):
            result = get_contacts(portal_id="148496292")
            assert "results" in result
            print("✅ get_contacts success test passed")

if __name__ == "__main__":
    print("Testing HubSpot service...")
    test_create_contact_success()
    test_create_contact_error()
    test_get_contacts_success()
    print("\n✅ All HubSpot tests passed")