# from fastapi import FastAPI, Request
# import httpx
# import os
# from dotenv import load_dotenv

# load_dotenv()

# app = FastAPI()

# token = os.getenv("HUBSPOT_ACCESS_TOKEN")
# headers = {
#     "Authorization": f"Bearer {token}",
#     "Content-Type": "application/json"
# }

# def calculate_score(properties: dict) -> int:
#     score = 0
#     source = properties.get("lead_source_custom", "")
#     if source == "referral":
#         score += 40
#     elif source == "google_ads":
#         score += 30
#     elif source == "facebook_ads":
#         score += 20
#     elif source == "organic":
#         score += 10
#     if properties.get("first_deal_created_date"):
#         score += 30
#     stage = properties.get("lifecyclestage", "")
#     if stage == "opportunity":
#         score += 30
#     elif stage == "lead":
#         score += 10
#     return score

# @app.post("/webhook")
# async def receive_webhook(request: Request):
#     payload = await request.json()
#     print("Webhook reçu:", payload)

#     for event in payload:
#         if event.get("subscriptionType") == "contact.creation":
#             contact_id = str(event.get("objectId"))
#             print(f"Nouveau contact détecté : {contact_id}")

#             # Récupérer les propriétés du contact
#             response = httpx.get(
#                 f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
#                 headers=headers,
#                 params={
#                     "properties": "lead_source_custom,lifecyclestage,first_deal_created_date"
#                 }
#             )

#             properties = response.json().get("properties", {})
#             score = calculate_score(properties)
#             print(f"Score calculé : {score}/100")

#             # Enregistrer le score
#             httpx.patch(
#                 f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
#                 headers=headers,
#                 json={"properties": {"lead_score_custom": score}}
#             )
#             print(f"Score enregistré pour contact {contact_id}")

#     return {"status": "ok"}

# @app.get("/webhook")
# async def verify_webhook():
#     return {"status": "webhook endpoint actif"}