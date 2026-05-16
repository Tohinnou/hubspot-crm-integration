# import httpx
# import os
# import json
# from datetime import datetime, timedelta
# from dotenv import load_dotenv

# load_dotenv()

# CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
# CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")

# # Stockage simple en JSON pour l'apprentissage
# # En production → PostgreSQL
# TOKEN_FILE = "tokens.json"

# def save_tokens(portal_id: str, access_token: str, refresh_token: str, expires_in: int):
#     tokens = load_all_tokens()
#     tokens[portal_id] = {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat()
#     }
#     with open(TOKEN_FILE, "w") as f:
#         json.dump(tokens, f, indent=2)
#     print(f"Tokens sauvegardés pour portal {portal_id}")
    
# def load_all_tokens() -> dict:
#     if not os.path.exists(TOKEN_FILE):
#         return {}
#     with open(TOKEN_FILE, "r") as f:
#         return json.load(f)
      
# def get_valid_token(portal_id: str) -> str:
#     tokens = load_all_tokens()
#     if portal_id not in tokens:
#         raise Exception(f"Aucun token pour portal {portal_id}")

#     token_data = tokens[portal_id]
#     expires_at = datetime.fromisoformat(token_data["expires_at"])

#     # Token expiré → refresh automatique
#     if datetime.now() >= expires_at:
#         print(f"Token expiré pour {portal_id} — refresh en cours...")
#         return refresh_access_token(portal_id, token_data["refresh_token"])

#     return token_data["access_token"]
  
# def refresh_access_token(portal_id: str, refresh_token: str) -> str:
#     response = httpx.post(
#         "https://api.hubapi.com/oauth/v1/token",
#         data={
#             "grant_type": "refresh_token",
#             "client_id": CLIENT_ID,
#             "client_secret": CLIENT_SECRET,
#             "refresh_token": refresh_token
#         }
#     )

#     tokens = response.json()
#     new_access_token = tokens["access_token"]
#     new_refresh_token = tokens.get("refresh_token", refresh_token)
#     expires_in = tokens["expires_in"]

#     save_tokens(portal_id, new_access_token, new_refresh_token, expires_in)
#     print(f"Token rafraîchi pour portal {portal_id}")
#     return new_access_token


# # Test
# if __name__ == "__main__":
#     # Simuler une sauvegarde
#     save_tokens(
#         portal_id="148498291",
#         access_token="test_access_token",
#         refresh_token="test_refresh_token",
#         expires_in=21600  # 6 heures
#     )

#     # Récupérer le token valide
#     token = get_valid_token("148498291")
#     print(f"Token récupéré : {token[:20]}...")