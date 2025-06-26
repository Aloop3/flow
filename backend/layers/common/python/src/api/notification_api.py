import logging
from src.services.notification_service import NotificationService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors

logger = logging.getLogger()
logger.setLevel(logging.INFO)

notification_service = NotificationService()


@with_middleware([log_request, handle_errors])
def get_notifications(event, context):
    """
    Handle GET /notifications request to get notifications for authenticated coach
    """
    try:
        # Extract coach_id from JWT claims
        user_id = (
            event.get("requestContext", {})
            .get("authorizer", {})
            .get("claims", {})
            .get("sub")
        )

        if not user_id:
            logger.error("No user ID found in request context")
            return create_response(401, {"error": "Unauthorized"})

        # Get query parameters
        query_params = event.get("queryStringParameters") or {}
        limit = query_params.get("limit")
        unread_only = query_params.get("unread_only", "false").lower() == "true"
        grouped = query_params.get("grouped", "false").lower() == "true"

        # Convert limit to int if provided
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                return create_response(400, {"error": "Invalid limit parameter"})

        logger.info(
            f"Getting notifications for coach {user_id}, limit={limit}, unread_only={unread_only}, grouped={grouped}"
        )

        if grouped:
            # Return notifications grouped by athlete
            notifications = notification_service.get_notifications_grouped_by_athlete(
                user_id, limit
            )
            # Convert nested notification objects to dicts
            result = {}
            for athlete_id, athlete_notifications in notifications.items():
                result[athlete_id] = [n.to_dict() for n in athlete_notifications]
            return create_response(200, result)
        else:
            # Return flat list of notifications
            notifications = notification_service.get_notifications_for_coach(
                user_id, limit, unread_only
            )
            return create_response(
                200, [notification.to_dict() for notification in notifications]
            )

    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def mark_notification_as_read(event, context):
    """
    Handle PATCH /notifications/{notification_id}/read request to mark notification as read
    """
    try:
        # Extract coach_id from JWT claims for authorization
        user_id = (
            event.get("requestContext", {})
            .get("authorizer", {})
            .get("claims", {})
            .get("sub")
        )

        if not user_id:
            logger.error("No user ID found in request context")
            return create_response(401, {"error": "Unauthorized"})

        # Extract notification_id from path parameters
        notification_id = event["pathParameters"]["notification_id"]

        logger.info(
            f"Marking notification {notification_id} as read for user {user_id}"
        )

        # Get the notification to verify ownership
        notification = notification_service.get_notification(notification_id)

        if not notification:
            return create_response(404, {"error": "Notification not found"})

        # Verify that the authenticated user is the coach for this notification
        if notification.coach_id != user_id:
            logger.warning(
                f"User {user_id} attempted to mark notification {notification_id} as read, but coach_id is {notification.coach_id}"
            )
            return create_response(403, {"error": "Forbidden"})

        # Mark as read
        success = notification_service.mark_notification_as_read(notification_id)

        if success:
            return create_response(200, {"message": "Notification marked as read"})
        else:
            return create_response(
                500, {"error": "Failed to mark notification as read"}
            )

    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return create_response(500, {"error": str(e)})
