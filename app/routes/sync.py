from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import SyncEvent, get_db
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])


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

    events = [
        {
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
        }
        for r in rows
    ]
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
