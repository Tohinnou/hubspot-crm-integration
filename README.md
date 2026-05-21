# HubSpot CRM Integration

Full-stack HubSpot CRM integration with a FastAPI backend, a React lead-capture form, and a live sync monitor with one-click replay of failed syncs.

OAuth 2.0 install flow, automatic lead scoring, real-time webhooks, retry with exponential backoff, and a Postgres-backed event log that lets you replay any failed HubSpot call from the dashboard.

## Screenshots

The dashboard combines the lead capture form with a live HubSpot sync monitor. Every API call is tracked; failed calls that have a captured payload can be replayed in one click.

![Dashboard with lead form, recent leads, and sync monitor showing Replay buttons on error rows](screenshots/replay-button-initial.png)

A successful replay shows a green confirmation and a new event row linked back to the original via a `↻ #N` badge:

![Successful replay with green flash and new SUCCESS row linked to event #9](screenshots/replay-flash-success.png)

When HubSpot rejects the replay (here: contact already exists from a previous successful retry), the real API error is surfaced in the dashboard instead of a generic "something went wrong":

![Failed replay with red flash showing the actual HubSpot error message](screenshots/replay-flash-error.png)

## Features

- **OAuth 2.0 install flow** — one-click install on any HubSpot account; tokens persist in Postgres, refresh automatically before expiry.
- **Lead capture API** — `POST /leads` validates and scores the lead, creates the contact in HubSpot, and returns the score in the response.
- **Lead scoring** — deterministic scoring on source, lifecycle, and deal association.
- **Retry with exponential backoff** — handles HubSpot 429 / 5xx automatically; non-retryable 4xx errors bubble up with a typed exception.
- **Sync monitor** — every HubSpot call is recorded with duration, status, error type, and a sanitized JSON payload. Surfaced as a dashboard with 24h KPIs and a per-event table.
- **One-click replay** — failed events with a captured payload can be re-executed from the UI. The new attempt is itself tracked and linked back to the original via `retried_from_id`.
- **Real-time webhooks** — `POST /webhook` accepts HubSpot events.
- **Multi-portal** — tokens are keyed by `portal_id`, so one backend can serve many HubSpot accounts.

## Architecture

```
┌─────────────────────────────┐
│  React frontend (port 3000) │
│  • Lead form                │
│  • Recent leads             │
│  • Sync Monitor + Replay    │
└──────────────┬──────────────┘
               │ HTTP
               ▼
┌─────────────────────────────┐         ┌──────────────────────┐
│  FastAPI backend (port 8000)│◀──HTTP──▶│   HubSpot API v3     │
│                             │         │  Contacts · Deals    │
│  • /oauth/*  /webhook       │         │  Properties · Search │
│  • /leads    /contacts      │         └──────────────────────┘
│  • /sync/events  /stats     │
│  • /sync/events/{id}/retry  │
└──────────────┬──────────────┘
               │ SQLAlchemy
               ▼
┌─────────────────────────────┐
│       PostgreSQL            │
│  • hubspot_tokens           │
│  • sync_events              │
└─────────────────────────────┘
```

Every HubSpot-bound call goes through `@track_sync`, which records duration, status, sanitized payload, and `retried_from_id` to `sync_events`. Replay reads the stored payload and dispatches through a whitelist (`RETRYABLE_OPERATIONS`) so a crafted operation name cannot reach arbitrary callables.

## Tech Stack

- **Backend** — Python 3.11+, FastAPI, SQLAlchemy 2.0, PostgreSQL, httpx
- **Frontend** — React 19 (Create React App)
- **Tests** — pytest

## Project Structure

```
crm-integration/
├── main.py                            # FastAPI entry point + CORS + router wiring
├── app/
│   ├── config.py                      # Env-based config (HubSpot, DB)
│   ├── database.py                    # SQLAlchemy engine, HubSpotToken, SyncEvent, migrations
│   ├── exceptions.py                  # HubSpotAPIError, RateLimitError
│   ├── logger.py                      # Structured logger setup
│   ├── routes/
│   │   ├── oauth.py                   # /oauth/install · /oauth/callback · /test/{portal_id}
│   │   ├── webhooks.py                # /webhook · /contacts · GET&POST /leads
│   │   └── sync.py                    # /sync/events · /sync/stats · /sync/events/{id}/retry
│   ├── services/
│   │   ├── hubspot.py                 # HubSpot API calls (decorated with @track_sync)
│   │   ├── hubspot_response.py        # Response parsing + error mapping
│   │   ├── retry.py                   # Exponential backoff for 429 / 5xx
│   │   ├── sync_tracker.py            # @track_sync decorator (payload capture + sanitize)
│   │   ├── token_db.py                # OAuth token persistence + refresh
│   │   └── lead_scorer.py             # Score calculation
│   └── models/
│       └── contact.py                 # Pydantic request/response models
├── frontend/lead-form/                # React app (lead form + dashboard + sync monitor)
└── tests/
    ├── test_hubspot.py
    ├── test_lead_scorer.py
    ├── test_retry.py
    ├── test_token_db.py
    └── test_webhook.py
```

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/Tohinnou/hubspot-crm-integration.git
cd hubspot-crm-integration
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/crm_integration
HUBSPOT_CLIENT_ID=your_oauth_client_id
HUBSPOT_CLIENT_SECRET=your_oauth_client_secret
HUBSPOT_REDIRECT_URI=http://localhost:8000/oauth/callback
```

### 3. Run the backend

```bash
uvicorn main:app --reload --port 8000
```

Tables and lightweight column-add migrations run on startup.

### 4. Run the frontend

```bash
cd frontend/lead-form
npm install
npm start
```

Open http://localhost:3000.

### 5. Connect a HubSpot account

Click **Install on HubSpot** in the header, approve the scopes, and you're back on the dashboard with a working token. Submit a lead and watch it land in HubSpot and in the Sync Monitor.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Health + endpoint listing |
| `GET`  | `/oauth/install` | Start OAuth flow |
| `GET`  | `/oauth/callback` | OAuth callback handler (saves tokens) |
| `GET`  | `/test/{portal_id}` | Verify the saved token works |
| `POST` | `/webhook` | Receive HubSpot events |
| `POST` | `/contacts` | Create a contact (raw passthrough) |
| `GET`  | `/leads` | List recent contacts from HubSpot (search API) |
| `POST` | `/leads` | Validate → score → create in HubSpot → return score |
| `GET`  | `/sync/events` | List recent sync events (filter by `status`, `operation`, `limit`) |
| `GET`  | `/sync/stats` | 24h KPIs: success rate, totals, avg latency, per-operation breakdown |
| `POST` | `/sync/events/{id}/retry` | Replay a failed sync from its stored payload |

## Lead Scoring

| Condition | Points |
|-----------|--------|
| Source: Referral | +40 |
| Source: Google Ads | +30 |
| Source: Facebook Ads | +20 |
| Source: Organic | +10 |
| Has associated deal | +30 |
| Lifecycle: Opportunity | +30 |
| Lifecycle: Lead | +10 |

## Sync Monitor & Replay

Every call decorated with `@track_sync("operation_name")` records:

- `duration_ms`, `status` (success/error), `error_type`, `error_message`
- `portal_id`, `contact_id` (resolved from response when not in args)
- `payload_json` — bound call arguments, recursively sanitized (secret-like keys are masked, oversized payloads are dropped at 8 KB)
- `retried_from_id` — set on replays, points back to the original event

`POST /sync/events/{id}/retry`:

- Loads the original event, validates it's a failed event with a stored payload
- Dispatches through `RETRYABLE_OPERATIONS` (whitelist of `create_contact`, `update_contact`, `score_contact`)
- Catches `HubSpotAPIError` → 502, `RateLimitError` → 429, unexpected → 500
- The new attempt is itself tracked via `@track_sync`, linked back through `retried_from_id`

The dashboard's Sync Monitor surfaces this with per-row Replay buttons, a green/red flash showing the actual API response, and auto-refresh of both the monitor and the recent-leads list on success.

## Error Handling

- `HubSpotAPIError(status, message, correlation_id)` — raised for non-2xx HubSpot responses
- `RateLimitError(retry_after)` — raised on 429
- `app/services/retry.py` retries 429 / 5xx with exponential backoff; 4xx (other than 429) is non-retryable and bubbles up immediately
- FastAPI routes translate these into 400 / 429 / 502 with structured JSON

## Running Tests

```bash
pytest -q
```

Coverage spans lead scoring, the retry mechanism, HubSpot service calls (with mocked httpx), and OAuth token DB persistence.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Postgres connection string | Yes |
| `HUBSPOT_CLIENT_ID` | OAuth app client ID | Yes |
| `HUBSPOT_CLIENT_SECRET` | OAuth app client secret | Yes |
| `HUBSPOT_REDIRECT_URI` | OAuth callback URL | Yes |
| `HUBSPOT_ACCESS_TOKEN` | Private App token (fallback when not using OAuth) | No |

## License

MIT
