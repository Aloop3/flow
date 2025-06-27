import uuid
from typing import Dict, List, Optional
from src.repositories.notification_repository import NotificationRepository
from src.repositories.user_repository import UserRepository
from src.services.relationship_service import RelationshipService
from src.models.notification import Notification
from src.models.workout import Workout


class NotificationService:
    def __init__(self):
        self.notification_repository = NotificationRepository()
        self.user_repository = UserRepository()
        self.relationship_service = RelationshipService()

    def create_workout_completion_notification(self, workout: Workout) -> bool:
        """
        Create a workout completion notification for the coach

        :param workout: The completed workout object
        :return: True if notification created successfully, False otherwise
        """
        try:
            # Get athlete information
            athlete_data = self.user_repository.get_user(workout.athlete_id)
            if not athlete_data:
                return False

            athlete_name = athlete_data.get("name", "Unknown Athlete")

            # Find the coach using relationship service instead of direct coach_id
            # Use the repository method directly since service doesn't expose this method
            relationship_data = self.relationship_service.relationship_repository.get_active_relationship_for_athlete(
                workout.athlete_id
            )

            if not relationship_data:
                return True  # Not an error, just no coach to notify

            coach_id = relationship_data.get("coach_id")

            # Verify coach exists
            coach_data = self.user_repository.get_user(coach_id)
            if not coach_data:
                return False

            # Create day info string
            day_info = f"Day {workout.day_id}" if workout.day_id else "Workout"
            if workout.date:
                day_info += f" ({workout.date})"

            # Create notification
            notification = Notification(
                notification_id=str(uuid.uuid4()),
                coach_id=coach_id,
                athlete_id=workout.athlete_id,
                athlete_name=athlete_name,
                workout_id=workout.workout_id,
                day_info=day_info,
                workout_data=workout.to_dict(),  # Store full workout data for modal
                is_read=False,
                notification_type="workout_completion",
            )

            # Save notification to repository
            return self.notification_repository.create_notification(
                notification.to_dict()
            )

        except Exception as e:
            # Log error but don't break workout completion
            print(f"Error creating workout completion notification: {str(e)}")
            return False

    def get_notifications_for_coach(
        self, coach_id: str, limit: int = None, unread_only: bool = False
    ) -> List[Notification]:
        """
        Get notifications for a specific coach

        :param coach_id: ID of the coach
        :param limit: Maximum number of notifications to return
        :param unread_only: If True, only return unread notifications
        :return: List of Notification objects
        """
        notification_data = self.notification_repository.get_notifications_for_coach(
            coach_id, limit, unread_only
        )

        notifications = []
        for data in notification_data:
            try:
                notification = Notification.from_dict(data)
                notifications.append(notification)
            except Exception:
                # Skip invalid notification data
                continue

        return notifications

    def get_notifications_grouped_by_athlete(
        self, coach_id: str, limit: int = None
    ) -> Dict[str, List[Notification]]:
        """
        Get notifications for a coach, grouped by athlete

        :param coach_id: ID of the coach
        :param limit: Maximum number of notifications to return
        :return: Dictionary with athlete_id as key and list of notifications as value
        """
        notifications = self.get_notifications_for_coach(coach_id, limit)

        grouped = {}
        for notification in notifications:
            athlete_id = notification.athlete_id
            if athlete_id not in grouped:
                grouped[athlete_id] = []
            grouped[athlete_id].append(notification)

        # Sort each athlete's notifications by creation time (newest first)
        for athlete_id in grouped:
            try:
                grouped[athlete_id].sort(key=lambda x: x.created_at, reverse=True)
            except Exception:
                # Fallback: sort by notification_id if created_at sorting fails
                grouped[athlete_id].sort(key=lambda x: x.notification_id, reverse=True)

        return grouped

    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """
        Get a single notification by ID

        :param notification_id: ID of the notification
        :return: Notification object if found, None otherwise
        """
        notification_data = self.notification_repository.get_notification(
            notification_id
        )
        if notification_data:
            try:
                return Notification.from_dict(notification_data)
            except Exception:
                return None
        return None

    def mark_notification_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read

        :param notification_id: ID of the notification to mark as read
        :return: True if successfully marked as read, False otherwise
        """
        return self.notification_repository.mark_notification_as_read(notification_id)

    def get_unread_count_for_coach(self, coach_id: str) -> int:
        """
        Get count of unread notifications for a coach

        :param coach_id: ID of the coach
        :return: Number of unread notifications
        """
        return self.notification_repository.get_unread_count_for_coach(coach_id)
