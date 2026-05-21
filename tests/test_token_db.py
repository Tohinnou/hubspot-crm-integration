import sys
sys.path.append(".")

from app.services.token_db import save_tokens_db, get_valid_token_db
from app.database import SessionLocal, HubSpotToken

TEST_PORTAL = "test_portal_db_123"

def test_save_and_retrieve_token():
    # Sauvegarder un token
    save_tokens_db(
        portal_id=TEST_PORTAL,
        access_token="test_access_token_db",
        refresh_token="test_refresh_token_db",
        expires_in=3600
    )
    
    # Récupérer le token
    token = get_valid_token_db(TEST_PORTAL)
    assert token == "test_access_token_db"
    print(f"✅ Token saved and retrieved from PostgreSQL")

def test_update_existing_token():
    # Mettre à jour le token existant
    save_tokens_db(
        portal_id=TEST_PORTAL,
        access_token="updated_access_token",
        refresh_token="updated_refresh_token",
        expires_in=3600
    )
    
    token = get_valid_token_db(TEST_PORTAL)
    assert token == "updated_access_token"
    print(f"✅ Token updated correctly in PostgreSQL")

def test_missing_portal_raises_error():
    try:
        get_valid_token_db("nonexistent_portal_xyz")
        print("❌ Should have raised Exception")
    except Exception as e:
        print(f"✅ Missing portal raises error correctly: {e}")

def cleanup():
    db = SessionLocal()
    try:
        db.query(HubSpotToken).filter(
            HubSpotToken.portal_id == TEST_PORTAL
        ).delete()
        db.commit()
        print("✅ Test data cleaned up")
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing PostgreSQL token storage...")
    test_save_and_retrieve_token()
    test_update_existing_token()
    test_missing_portal_raises_error()
    cleanup()
    print("\n✅ All PostgreSQL token tests passed")