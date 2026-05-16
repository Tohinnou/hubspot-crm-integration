# import httpx
# import os
# from dotenv import load_dotenv

# load_dotenv()

# token = os.getenv("HUBSPOT_ACCESS_TOKEN")

# headers = {"Authorization": f"Bearer {token}"}

# def calculate_score(properties: dict) -> int:
#   score = 0
  
#   source  = properties.get("lead_source_custom", "")
  
#   if source == "referral":
#     score += 40
#   elif source == "google_ads":
#     score +=30
#   elif source == "facebook_ads":
#         score += 20
#   elif source == "organic":
#         score += 10
        
#   #Has a associate deal
#   if properties.get("first_deal_created_date", ""):
#     score += 30
    
#   # Lifecycle stage
#   stage = properties.get("lifecyclestage", "")
#   if stage == "opportunity":
#     score += 30
#   elif stage == "lead":
#     score += 10
    
#   return score

# def update_lead_score(contact_id: str):
#     response = httpx.get(
#       f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
#       headers=headers,
#       params={
#         "properties": "lead_source_custom,lifecyclestage,first_deal_created_date"
#       }
#     )
    
#     contact = response.json()
#     properties = contact.get("properties", {})
  
  
#   # Calculer le score
#     score = calculate_score(properties)
#     print(f"Score calculé : {score}/100")

#     # Mettre à jour le contact
#     update_response = httpx.patch(
#         f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
#         headers=headers,
#         json={"properties": {"lead_score_custom": score}}
#     )

#     print("Status update:", update_response.status_code)
#     print("Lead score enregistré:", update_response.json().get("properties", {}).get("lead_score_custom"))
    
# update_lead_score("778835974361")