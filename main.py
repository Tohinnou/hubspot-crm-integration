from fastapi import FastAPI
from app.routes.oauth import router as oauth_router
from app.routes.webhooks import router as webhook_router
from app.routes.sync import router as sync_router
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables

app = FastAPI(
    title="HubSpot CRM Integration",
    description="API d'intégration HubSpot — Contacts, Deals, OAuth, Webhooks",
    version="1.0.0"
)

create_tables()

# CORS — autoriser React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(oauth_router)
app.include_router(webhook_router)
app.include_router(sync_router)

@app.get("/")
def root():
    return {
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/oauth/install",
            "/oauth/callback",
            "/test/{portal_id}",
            "/webhook",
            "/leads",
            "/sync/events",
            "/sync/stats",
        ]
    }