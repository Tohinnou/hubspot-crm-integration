from fastapi import APIRouter, Request
from app.services.hubspot import score_contact
from app.models.contact import ContactResponse, ContactCreate
from app.services.hubspot import create_contact

router = APIRouter()

@router.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    print("Webhook reçu:", payload)

    for event in payload:
        if event.get("subscriptionType") == "contact.creation":
            contact_id = str(event.get("objectId"))
            portal_id = str(event.get("portalId"))
            print(f"Nouveau contact : {contact_id} sur portal {portal_id}")

            score = score_contact(contact_id)
            print(f"Score enregistré : {score}/100")

    return {"status": "ok"}

@router.get("/webhook")
async def verify_webhook():
    return {"status": "webhook endpoint actif"}
  
@router.post("/contacts")
async def create_new_contact(contact: ContactCreate, portal_id: str = "148496292"):
    data = contact.model_dump(exclude_none=True)
    result = create_contact(data, portal_id)
    print("Réponse complète:", result)
    return {
        "id": result.get("id"),
        "status": "created"
    }