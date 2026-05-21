from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    HUBSPOT_ACCESS_TOKEN: str = os.getenv("HUBSPOT_ACCESS_TOKEN")
    HUBSPOT_CLIENT_ID: str = os.getenv("HUBSPOT_CLIENT_ID")
    HUBSPOT_CLIENT_SECRET: str = os.getenv("HUBSPOT_CLIENT_SECRET")
    HUBSPOT_REDIRECT_URI: str = os.getenv("HUBSPOT_REDIRECT_URI")
    TOKEN_FILE: str = "tokens.json"
    SCOPES: str = "crm.objects.contacts.read crm.objects.contacts.write crm.objects.deals.read crm.objects.deals.write"

settings = Settings()