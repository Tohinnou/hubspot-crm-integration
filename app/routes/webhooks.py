from fastapi import APIRouter, Request, Response
from app.services.hubspot import score_contact
from app.models.contact import ContactResponse, ContactCreate
from app.services.hubspot import create_contact
from app.exceptions import HubSpotAPIError, RateLimitError

from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    logger.info(f"Webhook received — {len(payload)} event(s)")

    for event in payload:
        if event.get("subscriptionType") == "contact.creation":
            contact_id = str(event.get("objectId"))
            portal_id = str(event.get("portalId"))
            logger.info(f"Nouveau contact : {contact_id} sur portal {portal_id}")

            score = score_contact(contact_id)
            logger.info(f"Score enregistré : {score}/100")
        if event.get("subscriptionType") == "contact.propertyChange":
          if event.get("propertyName") == "lifecyclestage":
              contact_id = str(event.get("objectId"))
              portal_id = str(event.get("portalId"))
              
              score = score_contact(contact_id, portal_id)

    return {"status": "ok"}

  
@router.post("/contacts")
async def create_new_contact(contact: ContactCreate, portal_id: str = "148496292"):
    data = contact.model_dump(exclude_none=True)
    result = create_contact(data, portal_id)
    print("Réponse complète:", result)
    return {
        "id": result.get("id"),
        "status": "created"
    }
    
@router.post("/leads")
async def capture_lead(contact: ContactCreate, portal_id: str = "148496292", response: Response = None):
    try:
        # 1. Créer le contact
        result = create_contact(contact.model_dump(exclude_none=True), portal_id)
        
        contact_id = result.get("id")
        if not contact_id:
            return {"status": "error", "message": result.get("message", "Unknown error")}

        # 2. Scorer immédiatement
        score = score_contact(contact_id, portal_id)

        return {
            "status": "success",
            "contact_id": contact_id,
            "name": f"{contact.firstname} {contact.lastname}",
            "email": contact.email,
            "lead_score": score,
            "message": f"Lead captured and scored successfully"
        }
    except RateLimitError:
        response.status_code = 429
        logger.warning("Rate limit hit on lead capture")
        return {"status": "error", "message": "Rate limit exceeded. Please try again later."}
    
    except HubSpotAPIError as e:
        response.status_code = 400
        logger.error(f"HubSpot API error during lead capture: {e.message} (status {e.status_code})")
        return {"status": "error", "message": f"HubSpot API error: {e.message}"}
    
    except Exception as e:
        response.status_code = 500
        logger.error(f"Unexpected error during lead capture: {str(e)}")
        return {"status": "error", "message": "An unexpected error occurred. Please try again later."}