import boto3
from typing import Dict, List, Any, Optional
from boto3.dynamodb.conditions import Key
from src.config.notification_config import NotificationConfig


class NotificationRepository:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.table_name = NotificationConfig.TABLE_NAME
        self.table = self.dynamodb.Table(self.table_name)

    def create_notification(self, notification_data: Dict[str, Any]) -> bool:
        """
        Create a new notification in DynamoDB

        :param notification_data: The notification data to create
        :return: True if successful, False otherwise
        """
        try:
            self.table.put_item(Item=notification_data)
            return True
        except Exception:
            return False

    def get_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific notification by ID

        :param notification_id: The ID of the notification to retrieve
        :return: The notification data if found, else None
        """
        try:
            response = self.table.get_item(Key={"notification_id": notification_id})
            return response.get("Item")
        except Exception:
            return None

    def get_notifications_for_coach(
        self, coach_id: str, limit: int = None, unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a specific coach, ordered by creation time (newest first)

        :param coach_id: The ID of the coach
        :param limit: Maximum number of notifications to return
        :param unread_only: If True, only return unread notifications
        :return: List of notification data dictionaries
        """
        try:
            # Use default limit from config if not provided
            if limit is None:
                limit = NotificationConfig.MAX_ITEMS

            # Use GSI to query by coach_id and sort by created_at
            query_kwargs = {
                "IndexName": NotificationConfig.COACH_INDEX,
                "KeyConditionExpression": Key("coach_id").eq(coach_id),
                "ScanIndexForward": False,  # Newest first
                "Limit": limit,
            }

            # Add filter for unread notifications if requested
            if unread_only:
                query_kwargs["FilterExpression"] = Key("is_read").eq(False)

            response = self.table.query(**query_kwargs)
            return response.get("Items", [])

        except Exception:
            return []

    def update_notification(
        self, notification_id: str, update_data: Dict[str, Any]
    ) -> bool:
        """
        Update a notification by notification_id

        :param notification_id: The ID of the notification to update
        :param update_data: The data to update the notification with
        :return: True if successful, False otherwise
        """
        try:
            # Build update expression dynamically
            update_expression_parts = []
            expression_attribute_values = {}

            for key, value in update_data.items():
                update_expression_parts.append(f"{key} = :{key}")
                expression_attribute_values[f":{key}"] = value

            update_expression = "SET " + ", ".join(update_expression_parts)

            self.table.update_item(
                Key={"notification_id": notification_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )
            return True
        except Exception:
            return False

    def mark_notification_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read

        :param notification_id: The ID of the notification to mark as read
        :return: True if successful, False otherwise
        """
        return self.update_notification(notification_id, {"is_read": True})

    def get_unread_count_for_coach(self, coach_id: str) -> int:
        """
        Get count of unread notifications for a coach

        :param coach_id: The ID of the coach
        :return: Number of unread notifications
        """
        try:
            response = self.table.query(
                IndexName=NotificationConfig.COACH_INDEX,
                KeyConditionExpression=Key("coach_id").eq(coach_id),
                FilterExpression=Key("is_read").eq(False),
                Select="COUNT",
            )
            return response.get("Count", 0)
        except Exception:
            return 0

    def delete_notification(self, notification_id: str) -> bool:
        """
        Delete a notification (for future cleanup functionality)

        :param notification_id: The ID of the notification to delete
        :return: True if successful, False otherwise
        """
        try:
            self.table.delete_item(Key={"notification_id": notification_id})
            return True
        except Exception:
            return False
