# HubSpot CRM Integration API

A production-ready FastAPI backend for HubSpot CRM automation — contacts, deals, lead scoring, OAuth 2.0, and real-time webhooks.

## Features

- **OAuth 2.0** — Install on any HubSpot account with one click
- **Contact Management** — Create, read, and update contacts via API
- **Deal Pipeline** — Create deals and associate them with contacts
- **Lead Scoring** — Automatic score calculation based on source, stage, and activity
- **Real-time Webhooks** — React to HubSpot events instantly
- **Custom Properties** — Extend HubSpot data model with business-specific fields
- **Multi-portal Support** — Manage multiple HubSpot accounts simultaneously


## Architecture

```
┌─────────────────┐         ┌──────────────────────┐
│   React Form    │──POST──▶│   FastAPI Backend    │
│  (port 3000)    │         │    (port 8000)        │
└─────────────────┘         └──────────┬───────────┘
                                        │
                             ┌──────────▼───────────┐
                             │   HubSpot API v3     │
                             │                      │
                             │  • Contacts CRUD     │
                             │  • Deals Pipeline    │
                             │  • Custom Properties │
                             │  • Webhooks          │
                             └──────────────────────┘

OAuth 2.0 Flow:
Client Browser ──▶ /oauth/install ──▶ HubSpot Authorize
                                              │
                                    /oauth/callback
                                              │
                                    save_tokens_db()
```

## Tech Stack

- **Python 3.11+**
- **FastAPI** — REST API framework
- **httpx** — Async HTTP client
- **Pydantic** — Data validation
- **HubSpot API v3**

## Project Structure

```
crm-integration/
├── main.py                 # Entry point
├── app/
│   ├── config.py           # Environment configuration
│   ├── routes/
│   │   ├── oauth.py        # OAuth 2.0 endpoints
│   │   └── webhooks.py     # Webhook handlers + CRM endpoints
│   ├── database.py         # SQLAlchemy engine + HubSpotToken model
│   ├── services/
│   │   ├── hubspot.py      # HubSpot API calls
│   │   ├── token_db.py     # OAuth token DB storage & refresh
│   │   └── lead_scorer.py  # Lead scoring logic
│   └── models/
│       └── contact.py      # Pydantic models
└── tests/
    ├── test_connection.py
    └── test_webhook.py
```

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/yourusername/crm-integration.git
cd crm-integration
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your HubSpot credentials:
HUBSPOT_ACCESS_TOKEN=your_private_app_token
HUBSPOT_CLIENT_ID=your_oauth_client_id
HUBSPOT_CLIENT_SECRET=your_oauth_client_secret
HUBSPOT_REDIRECT_URI=http://localhost:8000/oauth/callback

### 3. Run the server

```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/oauth/install` | Start OAuth flow |
| GET | `/oauth/callback` | OAuth callback handler |
| GET | `/test/{portal_id}` | Test connection |
| POST | `/contacts` | Create a contact |
| POST | `/webhook` | Receive HubSpot events |

## OAuth Flow
GET /oauth/install
→ Redirects to HubSpot authorization page
→ Client approves
→ HubSpot calls /oauth/callback?code=xxx
→ Tokens saved automatically per portal_id

## Lead Scoring Logic

| Condition | Points |
|-----------|--------|
| Source: Referral | +40 |
| Source: Google Ads | +30 |
| Source: Facebook Ads | +20 |
| Source: Organic | +10 |
| Has associated deal | +30 |
| Lifecycle: Opportunity | +30 |
| Lifecycle: Lead | +10 |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `HUBSPOT_ACCESS_TOKEN` | Private App token | Yes |
| `HUBSPOT_CLIENT_ID` | OAuth app client ID | Yes |
| `HUBSPOT_CLIENT_SECRET` | OAuth app client secret | Yes |
| `HUBSPOT_REDIRECT_URI` | OAuth callback URL | Yes |

## Use Cases

This integration solves real business problems:

- **Lead capture** — Automatically create HubSpot contacts from any form or source
- **Pipeline automation** — Open deals instantly when leads qualify
- **Real-time scoring** — Score leads the moment they enter the CRM
- **Multi-account management** — One codebase, multiple client HubSpot accounts

## License

MIT