# import httpx
# import os
# from dotenv import load_dotenv

# load_dotenv()

# token = os.getenv("HUBSPOT_ACCESS_TOKEN")
# headers = {
#     "Authorization": f"Bearer {token}",
#     "Content-Type": "application/json"
# }

# # Créer un nouveau contact pour déclencher le webhook
# new_contact = {
#     "properties": {
#         "firstname": "Webhook",
#         "lastname": "Test",
#         "email": "webhook.test@example.com",
#         "lead_source_custom": "google_ads"
#     }
# }

# response = httpx.post(
#     "https://api.hubapi.com/crm/v3/objects/contacts",
#     headers=headers,
#     json=new_contact
# )

# print("Status:", response.status_code)
# print("Contact ID:", response.json().get("id"))
# print("Attends 5-10 secondes et regarde ton terminal FastAPI...")