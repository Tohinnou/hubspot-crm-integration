import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import SyncEvent, get_db
from app.exceptions import HubSpotAPIError, RateLimitError
from app.logger import setup_logger
from app.services import hubspot

logger = setup_logger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])

# Whitelist of operations that can be replayed. Maps the stored operation name
# to the wrapped service function. New tracked operations must be added here
# explicitly — defence in depth so a malicious payload can't dispatch to
# arbitrary callables.
RETRYABLE_OPERATIONS = {
    "create_contact": hubspot.create_contact,
    "update_contact": hubspot.update_contact,
    "score_contact": hubspot.score_contact,
}


def _serialize_event(r: SyncEvent) -> dict:
    return {
        "id": r.id,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "operation": r.operation,
        "portal_id": r.portal_id,
        "contact_id": r.contact_id,
        "status": r.status,
        "duration_ms": r.duration_ms,
        "retry_count": r.retry_count,
        "error_type": r.error_type,
        "error_message": r.error_message,
        "retried_from_id": r.retried_from_id,
        "replayable": bool(
            r.status == "error"
            and r.payload_json
            and r.operation in RETRYABLE_OPERATIONS
        ),
    }


@router.get("/events")
def list_events(
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, pattern="^(success|error)$"),
    operation: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List recent sync events, newest first."""
    q = db.query(SyncEvent)
    if status:
        q = q.filter(SyncEvent.status == status)
    if operation:
        q = q.filter(SyncEvent.operation == operation)
    rows = q.order_by(SyncEvent.created_at.desc()).limit(limit).all()

    events = [_serialize_event(r) for r in rows]
    return {"status": "ok", "count": len(events), "events": events}


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Last-24h KPIs: total, success/error counts, success rate, avg latency,
    and per-operation breakdown."""
    since = datetime.now() - timedelta(hours=24)
    base = db.query(SyncEvent).filter(SyncEvent.created_at >= since)

    total = base.count()
    success_count = base.filter(SyncEvent.status == "success").count()
    error_count = base.filter(SyncEvent.status == "error").count()

    avg_duration = (
        db.query(func.avg(SyncEvent.duration_ms))
        .filter(SyncEvent.created_at >= since)
        .scalar()
    )
    avg_duration_ms = int(avg_duration) if avg_duration is not None else 0
    success_rate = round((success_count / total) * 100, 1) if total > 0 else 100.0

    per_op_rows = (
        db.query(
            SyncEvent.operation,
            func.count(SyncEvent.id).label("total"),
            func.sum(
                case((SyncEvent.status == "error", 1), else_=0)
            ).label("errors"),
        )
        .filter(SyncEvent.created_at >= since)
        .group_by(SyncEvent.operation)
        .all()
    )
    by_operation = [
        {"operation": op, "total": int(t or 0), "errors": int(e or 0)}
        for op, t, e in per_op_rows
    ]

    return {
        "status": "ok",
        "window_hours": 24,
        "total": total,
        "success_count": success_count,
        "error_count": error_count,
        "success_rate": success_rate,
        "avg_duration_ms": avg_duration_ms,
        "by_operation": by_operation,
    }


@router.post("/events/{event_id}/retry")
def retry_event(event_id: int, response: Response, db: Session = Depends(get_db)):
    """Replay a previously-failed sync. The new attempt creates its own
    SyncEvent row (via the @track_sync decorator) that points back to the
    original through `retried_from_id`."""
    original = db.query(SyncEvent).filter(SyncEvent.id == event_id).one_or_none()
    if original is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if original.status != "error":
        raise HTTPException(
            status_code=400, detail="Only failed events can be retried"
        )
    if not original.payload_json:
        raise HTTPException(
            status_code=400, detail="Event has no stored payload — cannot replay"
        )

    func_to_call = RETRYABLE_OPERATIONS.get(original.operation)
    if func_to_call is None:
        raise HTTPException(
            status_code=400,
            detail=f"Operation '{original.operation}' is not replayable",
        )

    try:
        payload = json.loads(original.payload_json)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Corrupt payload: {e}")

    logger.info(f"Retrying event {event_id} — operation: {original.operation}")
    try:
        result = func_to_call(_retried_from_id=event_id, **payload)
    except HubSpotAPIError as e:
        response.status_code = 502
        return {
            "status": "error",
            "message": f"HubSpot API error on retry: {e.message}",
            "retried_from_id": event_id,
        }
    except RateLimitError:
        response.status_code = 429
        return {
            "status": "error",
            "message": "Rate limit exceeded on retry",
            "retried_from_id": event_id,
        }
    except Exception as e:
        logger.error(f"Retry {event_id} failed unexpectedly: {e}")
        response.status_code = 500
        return {
            "status": "error",
            "message": "Unexpected error during retry",
            "retried_from_id": event_id,
        }

    # Pull the freshly-written event so the UI can show its id/status.
    new_event = (
        db.query(SyncEvent)
        .filter(SyncEvent.retried_from_id == event_id)
        .order_by(SyncEvent.id.desc())
        .first()
    )
    return {
        "status": "ok",
        "retried_from_id": event_id,
        "result": result if isinstance(result, (dict, int, str)) else None,
        "new_event": _serialize_event(new_event) if new_event else None,
    }
