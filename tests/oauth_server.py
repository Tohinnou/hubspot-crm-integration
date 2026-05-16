# from fastapi import FastAPI
# from fastapi.responses import RedirectResponse, HTMLResponse
# import httpx
# import os
# from dotenv import load_dotenv
# from tests.token_manager import save_tokens, get_valid_token


# load_dotenv()

# app = FastAPI()

# CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
# CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
# REDIRECT_URI = os.getenv("HUBSPOT_REDIRECT_URI")


# SCOPES = "crm.objects.contacts.read crm.objects.contacts.write crm.objects.deals.read crm.objects.deals.write"

# # Étape 1 — Rediriger vers HubSpot pour autorisation
# @app.get('/oauth/install')
# def install():
#     auth_url = (
#           f"https://app.hubspot.com/oauth/authorize"
#           f"?client_id={CLIENT_ID}"
#           f"&redirect_uri={REDIRECT_URI}"
#           f"&scope={SCOPES.replace(' ', '+')}"
#       )
#     return RedirectResponse(auth_url)


# # Étape 2 — HubSpot redirige ici avec le code
# @app.get("/oauth/callback")
# async def oauth_callback(code: str):
#     response=httpx.post(
#       'https://api.hubapi.com/oauth/v1/token',
#       data={
#             "grant_type": "authorization_code",
#             "client_id": CLIENT_ID,
#             "client_secret": CLIENT_SECRET,
#             "redirect_uri": REDIRECT_URI,
#             "code": code
#         }
#     )
    
#     tokens = response.json()
    
#     print("Tokens reçus:", tokens)

#     access_token = tokens.get("access_token")
#     refresh_token = tokens.get("refresh_token")
#     expires_in = tokens.get("expires_in")
    
#     # Récupérer le portal_id du compte connecté
#     portal_id = str(tokens["hub_id"])
    
#     save_tokens(portal_id, access_token, refresh_token, expires_in)
    
#     return HTMLResponse(f"""
#         <h2>OAuth réussi ✅</h2>
#         <p><b>Access Token:</b> {access_token[:20]}...</p>
#         <p><b>Refresh Token:</b> {refresh_token[:20]}...</p>
#         <p><b>Expire dans:</b> {expires_in} secondes</p>
#     """)

# @app.get("/test/{portal_id}")
# async def test_connection(portal_id: str):
#     # Récupérer un token valide (refresh automatique si expiré)
#     token = get_valid_token(portal_id)

#     response = httpx.get(
#         "https://api.hubapi.com/crm/v3/objects/contacts",
#         headers={"Authorization": f"Bearer {token}"}
#     )

#     contacts = response.json()
#     return {
#         "portal_id": portal_id,
#         "status": response.status_code,
#         "contacts_count": len(contacts.get("results", []))
#     }