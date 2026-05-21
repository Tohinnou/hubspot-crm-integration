from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import HubSpotToken, SessionLocal
from app.logger import setup_logger
import httpx
import os

logger = setup_logger(__name__)

CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")

def save_tokens_db(portal_id: str, access_token: str, refresh_token: str, expires_in: int):
    """Save or update OAuth tokens for a portal in PostgreSQL."""
    db: Session = SessionLocal()
    try:
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        token = db.query(HubSpotToken).filter(
            HubSpotToken.portal_id == portal_id
        ).first()
        
        if token:
            token.access_token = access_token
            token.refresh_token = refresh_token
            token.expires_at = expires_at
            token.updated_at = datetime.now()
            logger.info(f"Tokens updated for portal {portal_id}")
        else:
            token = HubSpotToken(
                portal_id=portal_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at
            )
            db.add(token)
            logger.info(f"Tokens created for portal {portal_id}")
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving tokens for portal {portal_id}: {e}")
        raise
    finally:
        db.close()

def get_valid_token_db(portal_id: str) -> str:
    """
    Get a valid access token for a portal.
    Automatically refreshes if expired.
    """
    db: Session = SessionLocal()
    try:
        token = db.query(HubSpotToken).filter(
            HubSpotToken.portal_id == portal_id
        ).first()
        
        if not token:
            logger.error(f"No token found for portal {portal_id}")
            raise Exception(f"No token found for portal {portal_id}")
        
        if datetime.now() >= token.expires_at:
            logger.warning(f"Token expired for portal {portal_id} — refreshing...")
            return refresh_token_db(portal_id, token.refresh_token)
        
        logger.debug(f"Valid token returned for portal {portal_id}")
        return token.access_token
    
    finally:
        db.close()

def refresh_token_db(portal_id: str, refresh_token: str) -> str:
    """Refresh an expired access token."""
    response = httpx.post(
        "https://api.hubapi.com/oauth/v1/token",
        data={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token
        }
    )
    
    tokens = response.json()
    new_access_token = tokens["access_token"]
    new_refresh_token = tokens.get("refresh_token", refresh_token)
    expires_in = tokens["expires_in"]
    
    save_tokens_db(portal_id, new_access_token, new_refresh_token, expires_in)
    logger.info(f"Token refreshed for portal {portal_id}")
    return new_access_token