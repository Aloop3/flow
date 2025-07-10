import logging
import time
from typing import Dict, Any, List
from src.middleware.middleware import ValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# In-memory storage for rate limiting
# Production: Consider Redis or DynamoDB for multi-lambda persistence
_rate_limit_cache: Dict[str, List[float]] = {}

# Rate limiting configuration
_requests_per_minute = 60
_window_size_seconds = 60


def rate_limit_user_requests(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Middleware to enforce per-user rate limiting.

    Implements sliding window rate limiting with 60 requests/minute limit.
    Tracks requests per user across all endpoints to prevent abuse.

    :param event: The Lambda event
    :param context: The Lambda context
    :return: The event, unchanged if within rate limit
    :raises: ValidationError if rate limit exceeded
    """
    # Extract user ID from JWT claims
    user_id = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("claims", {})
        .get("sub")
    )

    if not user_id:
        logger.error("No user ID found for rate limiting")
        # Don't block requests without user ID - let auth middleware handle
        return event

    current_time = time.time()

    try:
        # Check and update rate limit for user
        if _is_rate_limited(user_id, current_time):
            _log_rate_limit_violation(user_id, event)
            raise ValidationError("Rate limit exceeded - too many requests")

        # Add current request to user's window
        _record_request(user_id, current_time)

        # Log rate limit status for monitoring
        request_count = len(_rate_limit_cache.get(user_id, []))
        logger.info(
            f"Rate limit check: user={user_id[:8]}..., requests={request_count}/{_requests_per_minute}"
        )

    except ValidationError:
        raise  # Re-raise validation errors
    except Exception as e:
        logger.error(f"Error in rate limiting: {str(e)}")
        # Don't block requests on rate limiting failures
        # Just log and continue

    return event


def _is_rate_limited(user_id: str, current_time: float) -> bool:
    """
    Check if user has exceeded rate limit within sliding window.

    :param user_id: User identifier
    :param current_time: Current timestamp
    :return: True if rate limit exceeded, False otherwise
    """
    # Get user's request history
    user_requests = _rate_limit_cache.get(user_id, [])

    # Remove requests outside the time window
    window_start = current_time - _window_size_seconds
    recent_requests = [
        req_time for req_time in user_requests if req_time >= window_start
    ]

    # Update cache with filtered requests
    _rate_limit_cache[user_id] = recent_requests

    # Check if adding this request would exceed limit
    return len(recent_requests) >= _requests_per_minute


def _record_request(user_id: str, current_time: float) -> None:
    """
    Record current request timestamp for user.

    :param user_id: User identifier
    :param current_time: Current timestamp
    """
    if user_id not in _rate_limit_cache:
        _rate_limit_cache[user_id] = []

    _rate_limit_cache[user_id].append(current_time)


def _log_rate_limit_violation(user_id: str, event: Dict[str, Any]) -> None:
    """
    Log rate limit violation for monitoring and alerting.

    :param user_id: User who exceeded rate limit
    :param event: Lambda event for additional context
    """
    resource = event.get("resource", "unknown")
    method = event.get("httpMethod", "unknown")
    source_ip = (
        event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown")
    )
    user_agent = event.get("headers", {}).get("User-Agent", "unknown")

    logger.warning(
        f"RATE_LIMIT_VIOLATION: user={user_id}, "
        f"endpoint={method} {resource}, "
        f"ip={source_ip}, "
        f"user_agent={user_agent}, "
        f"limit={_requests_per_minute}/min"
    )


def _cleanup_expired_users() -> None:
    """
    Remove users with no recent requests to prevent memory leaks.

    Called periodically to clean up users who haven't made requests
    in the last window period.
    """
    current_time = time.time()
    window_start = current_time - _window_size_seconds
    expired_users = []

    for user_id, requests in _rate_limit_cache.items():
        # Remove expired requests
        recent_requests = [
            req_time for req_time in requests if req_time >= window_start
        ]

        if not recent_requests:
            # No recent requests - mark for removal
            expired_users.append(user_id)
        else:
            # Update with filtered requests
            _rate_limit_cache[user_id] = recent_requests

    # Remove expired users
    for user_id in expired_users:
        del _rate_limit_cache[user_id]

    if expired_users:
        logger.info(
            f"Cleaned {len(expired_users)} inactive users from rate limit cache"
        )


def get_rate_limit_stats() -> Dict[str, Any]:
    """
    Get current rate limiting statistics for monitoring.

    :return: Dictionary with rate limiting metrics
    """
    _cleanup_expired_users()

    total_users = len(_rate_limit_cache)
    total_requests = sum(len(requests) for requests in _rate_limit_cache.values())

    # Calculate users near rate limit (>80% of limit)
    near_limit_threshold = int(_requests_per_minute * 0.8)
    users_near_limit = sum(
        1
        for requests in _rate_limit_cache.values()
        if len(requests) >= near_limit_threshold
    )

    return {
        "active_users": total_users,
        "total_requests_in_window": total_requests,
        "users_near_limit": users_near_limit,
        "rate_limit": f"{_requests_per_minute}/min",
        "window_size": f"{_window_size_seconds}s",
        "cache_size_kb": len(str(_rate_limit_cache)) / 1024,
    }


def get_user_rate_limit_status(user_id: str) -> Dict[str, Any]:
    """
    Get rate limit status for specific user.

    :param user_id: User identifier
    :return: Dictionary with user's rate limit status
    """
    current_time = time.time()
    user_requests = _rate_limit_cache.get(user_id, [])

    # Filter to current window
    window_start = current_time - _window_size_seconds
    recent_requests = [
        req_time for req_time in user_requests if req_time >= window_start
    ]

    remaining_requests = max(0, _requests_per_minute - len(recent_requests))
    next_reset = None

    if recent_requests:
        # Next reset is when oldest request falls out of window
        oldest_request = min(recent_requests)
        next_reset = oldest_request + _window_size_seconds

    return {
        "user_id": user_id,
        "requests_used": len(recent_requests),
        "requests_remaining": remaining_requests,
        "rate_limit": _requests_per_minute,
        "window_size": _window_size_seconds,
        "next_reset": next_reset,
        "is_limited": len(recent_requests) >= _requests_per_minute,
    }
