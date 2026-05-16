import httpx
from app.config import settings
from app.services.token_manager import get_valid_token
from app.services.lead_scorer import calculate_score

def get_headers(portal_id: str = None) -> dict:
    if portal_id:
        try:
            token = get_valid_token(portal_id)
        except Exception:
            # Fallback sur le token statique de la Private App
            token = settings.HUBSPOT_ACCESS_TOKEN
    else:
        token = settings.HUBSPOT_ACCESS_TOKEN
        
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
def get_contacts(portal_id:str) -> dict:
    response = httpx.get(
        "https://api.hubapi.com/crm/v3/objects/contacts",
        headers=get_headers(portal_id)
    )
    return response.json()
  
def create_contact(properties: dict, portal_id: str = None) -> dict:
    response = httpx.post(
        "https://api.hubapi.com/crm/v3/objects/contacts",
        headers=get_headers(portal_id),
        json={"properties": properties}
    )
    return response.json()
  
def update_contact(contact_id: str, properties: dict, portal_id: str = None) -> dict:
    response = httpx.patch(
        f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
        headers=get_headers(portal_id),
        json={"properties": properties}
    )
    return response.json()
  
def get_contact_properties(contact_id: str, properties: list, portal_id: str = None) -> dict:
    response = httpx.get(
        f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
        headers=get_headers(portal_id),
        params={"properties": ",".join(properties)}
    )
    return response.json().get("properties", {})
  
def score_contact(contact_id: str, portal_id: str = None) -> int:
    properties = get_contact_properties(
        contact_id,
        ["lead_source_custom", "lifecyclestage", "first_deal_created_date"],
        portal_id
    )
    score = calculate_score(properties)
    update_contact(contact_id, {"lead_score_custom": score}, portal_id)
    return score