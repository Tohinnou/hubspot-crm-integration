import time
import functools
import inspect
from typing import Callable, Any, Optional

from app.database import SyncEvent, SessionLocal
from app.logger import setup_logger

logger = setup_logger(__name__)


def _save_event(
    operation: str,
    status: str,
    duration_ms: int,
    portal_id: Optional[str] = None,
    contact_id: Optional[str] = None,
    retry_count: int = 0,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    """Persist a SyncEvent row. Best-effort — must not raise into the caller."""
    try:
        db = SessionLocal()
        try:
            event = SyncEvent(
                operation=operation,
                portal_id=str(portal_id) if portal_id is not None else None,
                contact_id=str(contact_id) if contact_id is not None else None,
                status=status,
                duration_ms=duration_ms,
                retry_count=retry_count,
                error_type=error_type,
                error_message=error_message[:2000] if error_message else None,
            )
            db.add(event)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Failed to persist SyncEvent for {operation}: {e}")


def _extract_contact_id(result: Any) -> Optional[str]:
    if isinstance(result, dict):
        cid = result.get("id")
        if cid is not None:
            return str(cid)
    return None


def track_sync(operation: str) -> Callable:
    """Record sync events (duration + status + errors) to the SyncEvent table.

    Reads `portal_id` and `contact_id` from the wrapped call's bound arguments;
    if the wrapped function creates a contact, falls back to the response `id`.
    """
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            portal_id: Optional[Any] = None
            contact_id: Optional[Any] = None
            try:
                bound = sig.bind_partial(*args, **kwargs)
                portal_id = bound.arguments.get("portal_id")
                contact_id = bound.arguments.get("contact_id")
            except TypeError:
                pass

            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.perf_counter() - start) * 1000)
                if not contact_id:
                    contact_id = _extract_contact_id(result)
                _save_event(operation, "success", duration_ms, portal_id, contact_id)
                return result
            except Exception as e:
                duration_ms = int((time.perf_counter() - start) * 1000)
                _save_event(
                    operation, "error", duration_ms, portal_id, contact_id,
                    error_type=type(e).__name__, error_message=str(e),
                )
                raise

        return wrapper
    return decorator
