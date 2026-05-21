from fastapi import APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse
import httpx
from app.config import settings
from app.services.token_db import save_tokens_db
from app.services.hubspot import get_contacts

router = APIRouter()

@router.get("/oauth/install")
def install():
    auth_url = (
        f"https://app.hubspot.com/oauth/authorize"
        f"?client_id={settings.HUBSPOT_CLIENT_ID}"
        f"&redirect_uri={settings.HUBSPOT_REDIRECT_URI}"
        f"&scope={settings.SCOPES.replace(' ', '+')}"
    )
    return RedirectResponse(auth_url)

@router.get("/oauth/callback")
async def oauth_callback(code: str):
    response = httpx.post(
        "https://api.hubapi.com/oauth/v1/token",
        data={
            "grant_type": "authorization_code",
            "client_id": settings.HUBSPOT_CLIENT_ID,
            "client_secret": settings.HUBSPOT_CLIENT_SECRET,
            "redirect_uri": settings.HUBSPOT_REDIRECT_URI,
            "code": code
        }
    )
    tokens = response.json()
    portal_id = str(tokens["hub_id"])
    save_tokens_db(portal_id, tokens["access_token"], tokens["refresh_token"], tokens["expires_in"])

    return HTMLResponse(f"""
        <h2>Installation réussie ✅</h2>
        <p><b>Portal ID:</b> {portal_id}</p>
        <p><b>Expire dans:</b> {tokens["expires_in"] // 60} minutes</p>
    """)

@router.get("/test/{portal_id}")
async def test_connection(portal_id: str):
    contacts = get_contacts(portal_id)
    return {
        "portal_id": portal_id,
        "status": "ok",
        "contacts_count": len(contacts.get("results", []))
    }