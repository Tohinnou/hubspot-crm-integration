# import httpx
# import os
# from dotenv import load_dotenv

# load_dotenv()

# token = os.getenv("HUBSPOT_ACCESS_TOKEN")

# headers = {"Authorization": f"Bearer {token}"}

# new_contact = {
#     "properties": {
#         "firstname": "Test",
#         "lastname": "Upwork",
#         "email": "test.upwork@example.com",
#         "phone": "+22901000000"
#     }
# }
# # Create a new contact
# # Récupérer les contacts
# # response = httpx.post(
# #     "https://api.hubapi.com/crm/v3/objects/contacts",
# #     headers=headers,
# #     json=new_contact
# # )

# #Create a new Deal
# #A deal stores data about an ongoing transaction. 
# # The deals endpoints allow you to manage this data and sync it between HubSpot and other systems.

# new_deal = {
#     "properties": {
#         "dealname": "Deal Test Upwork",
#         "amount": "5000",
#         "dealstage": "appointmentscheduled",
#         "pipeline": "default",
#         "closedate": "2026-06-30"
#     }
# }

# # response = httpx.post(
# #     "https://api.hubapi.com/crm/v3/objects/deals",
# #     headers=headers,
# #     json=new_deal
# # )



# CONTACT_ID = "778835974361"  # Test Upwork
# DEAL_ID = "502748674266"     # Deal Test Upwork

# # response = httpx.put(
# #     f"https://api.hubapi.com/crm/v3/objects/deals/{DEAL_ID}/associations/contacts/{CONTACT_ID}/3",
# #     headers=headers
# # )

# # response = httpx.get(
# #     f"https://api.hubapi.com/crm/v3/objects/contacts/{CONTACT_ID}/associations/deals",
# #     headers=headers
# # )

# # Create a propertie "lead_source"
# # new_property = {
# #     "name": "lead_source_custom",
# #     "label": "Lead Source Custom",
# #     "type": "enumeration",
# #     "fieldType": "select",
# #     "groupName": "contactinformation",
# #     "options": [
# #         {"label": "Facebook Ads", "value": "facebook_ads", "displayOrder": 1},
# #         {"label": "Google Ads", "value": "google_ads", "displayOrder": 2},
# #         {"label": "Referral", "value": "referral", "displayOrder": 3},
# #         {"label": "Organic", "value": "organic", "displayOrder": 4}
# #     ]
# # }

# # response = httpx.post(
# #     "https://api.hubapi.com/crm/v3/properties/contacts",
# #     headers=headers,
# #     json=new_property
# # )

# #Create a lead_score properties
# new_property = {
#     "name": "lead_score_custom",
#     "label": "Lead Score",
#     "type": "number",
#     "fieldType": "number",
#     "groupName": "contactinformation",
#     "description": "Score calculé automatiquement selon le comportement du lead"
# }

# response = httpx.post(
#     "https://api.hubapi.com/crm/v3/properties/contacts",
#     headers=headers,
#     json=new_property
# )

# #Assign custom properties on contact
# # update = {
# #     "properties": {
# #         "lead_source_custom": "facebook_ads"
# #     }
# # }

# # response = httpx.patch(
# #     f"https://api.hubapi.com/crm/v3/objects/contacts/{CONTACT_ID}",
# #     headers=headers,
# #     json=update
# # )

# print("Status:", response.status_code)
# print("Contacts:", response.json())