from fastapi import FastAPI
from app.routes.oauth import router as oauth_router
from app.routes.webhooks import router as webhook_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HubSpot CRM Integration",
    description="API d'intégration HubSpot — Contacts, Deals, OAuth, Webhooks",
    version="1.0.0"
)

# CORS — autoriser React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(oauth_router)
app.include_router(webhook_router)

@app.get("/")
def root():
    return {
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/oauth/install",
            "/oauth/callback",
            "/test/{portal_id}",
            "/webhook"
        ]
    }