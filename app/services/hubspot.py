import httpx
from app.config import settings
from app.services.token_manager import get_valid_token
from app.services.lead_scorer import calculate_score
from app.services.hubspot_response import handle_response
from app.services.retry import with_retry

from app.logger import setup_logger

logger = setup_logger(__name__)

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
    return handle_response(response)
  
def create_contact(properties: dict, portal_id: str = None) -> dict:
    """
    Create a new contact in HubSpot CRM.
    
    Args:
        properties: Contact fields (firstname, lastname, email, etc.)
        portal_id: HubSpot portal ID. Uses default token if None.
    
    Returns:
        HubSpot API response with contact id and properties.
    """
    logger.info(f"Creating contact — email: {properties.get('email')} — portal: {portal_id}")

    def _call():
        response = httpx.post(
            "https://api.hubapi.com/crm/v3/objects/contacts",
            headers=get_headers(portal_id),
            json={"properties": properties}
        )
        return handle_response(response)
    
    return with_retry(_call)
   
def update_contact(contact_id: str, properties: dict, portal_id: str = None) -> dict:
    logger.info(f"Updating contact — ID: {contact_id} — portal: {portal_id}")
    
    def _call():
        response = httpx.patch(
            f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
            headers=get_headers(portal_id),
            json={"properties": properties}
        )
        return handle_response(response)

    return with_retry(_call)
  
def get_contact_properties(contact_id: str, properties: list, portal_id: str = None) -> dict:
    def _call():
        response = httpx.get(
            f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
            headers=get_headers(portal_id),
            params={"properties": ",".join(properties)}
        )
        return handle_response(response)

    return with_retry(_call)

def score_contact(contact_id: str, portal_id: str = None) -> int:

    """
    Calculate and save lead score for a contact.
    
    Scoring criteria:
        - Lead source (referral=40, google=30, facebook=20, organic=10)
        - Has associated deal (+30)
        - Lifecycle stage (opportunity=30, lead=10)
    
    Args:
        contact_id: HubSpot contact ID
        portal_id: HubSpot portal ID
    
    Returns:
        Calculated score (0-100)
    """
    
    logger.info(f"Scoring contact {contact_id}")

    properties = get_contact_properties(
        contact_id,
        ["lead_source_custom", "lifecyclestage", "first_deal_created_date"],
        portal_id
    )
    score = calculate_score(properties)
    update_contact(contact_id, {"lead_score_custom": score}, portal_id)
    logger.info(f"Contact {contact_id} scored: {score}/100")
    return score