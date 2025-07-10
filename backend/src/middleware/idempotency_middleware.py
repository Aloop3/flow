import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional
from src.middleware.middleware import ValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# In-memory cache for duplicate request detection
# Production: Replace with DynamoDB for multi-lambda persistence
_idempotency_cache: Dict[str, float] = {}
_cache_ttl_seconds = 300  # 5 minutes


def prevent_duplicate_requests(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Middleware to prevent duplicate POST requests within 5-minute window.

    Creates content-based hash of user_id + request body + endpoint
    to detect duplicate submissions for resource creation endpoints.

    :param event: The Lambda event
    :param context: The Lambda context
    :return: The event, unchanged if not duplicate
    :raises: ValidationError if duplicate request detected
    """
    method = event.get("httpMethod", "")
    resource = event.get("resource", "")

    # Only apply to resource creation endpoints
    creation_endpoints = [
        "/blocks",
        "/exercises",
        "/workouts",
        "/days",
        "/users",
        "/relationships",
    ]

    # Skip if not a POST request or not a creation endpoint
    if method != "POST" or not any(
        endpoint in resource for endpoint in creation_endpoints
    ):
        return event

    # Clean expired entries from cache
    _cleanup_cache()

    try:
        # Generate idempotency key
        idempotency_key = _generate_idempotency_key(event)

        # Check if request already exists
        if idempotency_key in _idempotency_cache:
            logger.warning(f"Duplicate request detected: {idempotency_key}")
            raise ValidationError("Duplicate request - please wait before retrying")

        # Store request fingerprint with timestamp
        _idempotency_cache[idempotency_key] = time.time()

        logger.info(f"Request registered for idempotency: {idempotency_key[:16]}...")

    except ValidationError:
        raise  # Re-raise validation errors
    except Exception as e:
        logger.error(f"Error in idempotency check: {str(e)}")
        # Don't block requests on idempotency failures
        # Just log and continue

    return event


def _generate_idempotency_key(event: Dict[str, Any]) -> str:
    """
    Generate unique hash for request based on user + content + endpoint.

    :param event: Lambda event
    :return: SHA-256 hash string for idempotency key
    """
    # Extract user ID from JWT claims
    user_id = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("claims", {})
        .get("sub", "unknown")
    )

    # Extract request details
    resource = event.get("resource", "")
    method = event.get("httpMethod", "")
    body = event.get("body", "")

    # Normalize request body for consistent hashing
    normalized_body = _normalize_request_body(body)

    # Create fingerprint string
    fingerprint_data = f"{user_id}:{method}:{resource}:{normalized_body}"

    # Generate SHA-256 hash
    return hashlib.sha256(fingerprint_data.encode("utf-8")).hexdigest()


def _normalize_request_body(body: str) -> str:
    """
    Normalize request body for consistent hashing.

    Handles JSON formatting differences and extracts only relevant fields
    that should trigger duplicate detection.

    :param body: Raw request body string
    :return: Normalized string representation
    """
    if not body:
        return ""

    try:
        # Parse JSON to normalize formatting
        parsed = json.loads(body)

        # Remove timestamp fields that shouldn't affect duplication
        exclude_fields = ["timestamp", "created_at", "updated_at", "request_id"]

        normalized = {}
        for key, value in parsed.items():
            if key not in exclude_fields:
                normalized[key] = value

        # Sort keys for consistent ordering
        return json.dumps(normalized, sort_keys=True, separators=(",", ":"))

    except json.JSONDecodeError:
        # If not valid JSON, use raw body
        return body.strip()


def _cleanup_cache() -> None:
    """
    Remove expired entries from idempotency cache.

    Entries older than TTL are removed to prevent memory leaks
    and allow legitimate retries after timeout period.
    """
    current_time = time.time()
    expired_keys = []

    for key, timestamp in _idempotency_cache.items():
        if current_time - timestamp > _cache_ttl_seconds:
            expired_keys.append(key)

    for key in expired_keys:
        del _idempotency_cache[key]

    if expired_keys:
        logger.info(f"Cleaned {len(expired_keys)} expired idempotency entries")


def get_cache_stats() -> Dict[str, Any]:
    """
    Get current cache statistics for monitoring.

    :return: Dictionary with cache metrics
    """
    _cleanup_cache()

    current_time = time.time()
    active_entries = len(_idempotency_cache)

    oldest_entry = None
    if _idempotency_cache:
        oldest_timestamp = min(_idempotency_cache.values())
        oldest_entry = current_time - oldest_timestamp

    return {
        "active_entries": active_entries,
        "ttl_seconds": _cache_ttl_seconds,
        "oldest_entry_age": oldest_entry,
        "cache_size_kb": len(str(_idempotency_cache)) / 1024,
    }
