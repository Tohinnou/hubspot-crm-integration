import time
import json
import functools
import inspect
from typing import Callable, Any, Optional, Dict

from app.database import SyncEvent, SessionLocal
from app.logger import setup_logger

logger = setup_logger(__name__)

_SECRET_KEY_HINTS = ("token", "secret", "password", "api_key", "apikey", "authorization")
_MAX_PAYLOAD_BYTES = 8000


def _is_secret_key(name: str) -> bool:
    n = name.lower()
    return any(hint in n for hint in _SECRET_KEY_HINTS)


def _sanitize(value: Any) -> Any:
    """Recursively strip secret-like keys and drop non-JSON values."""
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if _is_secret_key(str(k)):
                out[k] = "***"
            else:
                out[k] = _sanitize(v)
        return out
    if isinstance(value, (list, tuple)):
        return [_sanitize(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _serialize_payload(bound_arguments: Dict[str, Any]) -> Optional[str]:
    if not bound_arguments:
        return None
    try:
        clean = {k: _sanitize(v) for k, v in bound_arguments.items() if k != "self"}
        payload = json.dumps(clean, ensure_ascii=False)
        if len(payload) > _MAX_PAYLOAD_BYTES:
            return None
        return payload
    except (TypeError, ValueError):
        return None


def _save_event(
    operation: str,
    status: str,
    duration_ms: int,
    portal_id: Optional[str] = None,
    contact_id: Optional[str] = None,
    retry_count: int = 0,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
    payload_json: Optional[str] = None,
    retried_from_id: Optional[int] = None,
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
                payload_json=payload_json,
                retried_from_id=retried_from_id,
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
    """Record sync events (duration + status + errors + payload) to SyncEvent.

    Reads `portal_id` and `contact_id` from the wrapped call's bound arguments;
    if the wrapped function creates a contact, falls back to the response `id`.
    Captures the (sanitized) bound arguments as JSON so the call can be replayed.
    The retried-from id (when the call is a retry) is passed through kwargs
    via the reserved `_retried_from_id` key and is NOT forwarded to the wrapped
    function.
    """
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retried_from_id = kwargs.pop("_retried_from_id", None)
            start = time.perf_counter()
            portal_id: Optional[Any] = None
            contact_id: Optional[Any] = None
            payload_json: Optional[str] = None
            try:
                bound = sig.bind_partial(*args, **kwargs)
                bound.apply_defaults()
                portal_id = bound.arguments.get("portal_id")
                contact_id = bound.arguments.get("contact_id")
                payload_json = _serialize_payload(dict(bound.arguments))
            except TypeError:
                pass

            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.perf_counter() - start) * 1000)
                if not contact_id:
                    contact_id = _extract_contact_id(result)
                _save_event(
                    operation, "success", duration_ms, portal_id, contact_id,
                    payload_json=payload_json, retried_from_id=retried_from_id,
                )
                return result
            except Exception as e:
                duration_ms = int((time.perf_counter() - start) * 1000)
                _save_event(
                    operation, "error", duration_ms, portal_id, contact_id,
                    error_type=type(e).__name__, error_message=str(e),
                    payload_json=payload_json, retried_from_id=retried_from_id,
                )
                raise

        return wrapper
    return decorator
