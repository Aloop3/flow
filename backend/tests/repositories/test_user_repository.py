import unittest
from unittest.mock import MagicMock, patch
from src.repositories.user_repository import UserRepository


class TestUserRepository(unittest.TestCase):
    """
    Test suite for the UserRepository class
    """

    def setUp(self):
        """
        Set up test environment before each test
        """
        self.mock_table = MagicMock()
        self.mock_dynamodb = MagicMock()
        self.mock_dynamodb.Table.return_value = self.mock_table

        # Patch boto3.resource to return our mock
        self.patcher = patch("boto3.resource")
        self.mock_boto3 = self.patcher.start()
        self.mock_boto3.return_value = self.mock_dynamodb

        # Initialize repository with mocked resources
        self.repository = UserRepository()

    def tearDown(self):
        """
        Clean up after each test
        """
        self.patcher.stop()

    def test_get_user(self):
        """
        Test retrieving a user by ID
        """
        # Setup mock return value
        mock_user = {
            "user_id": "user123",
            "email": "user@example.com",
            "name": "Test User",
            "role": "athlete",
        }
        self.mock_table.get_item.return_value = {"Item": mock_user}

        # Call the method
        result = self.repository.get_user("user123")

        # Assert
        self.mock_table.get_item.assert_called_once_with(Key={"user_id": "user123"})
        self.assertEqual(result, mock_user)

    def test_get_user_not_found(self):
        """
        Test retrieving a non-existent user
        """
        # Setup mock return value for not found case
        self.mock_table.get_item.return_value = {}

        # Call the method
        result = self.repository.get_user("nonexistent")

        # Assert
        self.mock_table.get_item.assert_called_once_with(Key={"user_id": "nonexistent"})
        self.assertIsNone(result)

    def test_get_user_by_email(self):
        """
        Test retrieving a user by email address
        """
        # Setup mock return value
        mock_user = {
            "user_id": "user123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete",
        }
        self.mock_table.query.return_value = {"Items": [mock_user]}

        # Call the method
        result = self.repository.get_user_by_email("test@example.com")

        # Assert
        self.mock_table.query.assert_called_once_with(
            IndexName="email-index",
            KeyConditionExpression="email = :email",
            ExpressionAttributeValues={":email": "test@example.com"},
            Limit=1,
        )
        self.assertEqual(result, mock_user)

    def test_get_user_by_email_not_found(self):
        """
        Test retrieving a user by email when the email doesn't exist
        """
        # Setup mock return value for not found case
        self.mock_table.query.return_value = {"Items": []}

        # Call the method
        result = self.repository.get_user_by_email("nonexistent@example.com")

        # Assert
        self.mock_table.query.assert_called_once_with(
            IndexName="email-index",
            KeyConditionExpression="email = :email",
            ExpressionAttributeValues={":email": "nonexistent@example.com"},
            Limit=1,
        )
        self.assertIsNone(result)

    def test_get_user_by_email_multiple_results(self):
        """
        Test retrieving a user by email when multiple results are returned

        Although the database should enforce uniqueness on email addresses,
        this test verifies that the method returns only the first item if
        multiple items are returned for some reason.
        """
        # Setup mock return value with multiple items
        mock_users = [
            {
                "user_id": "user123",
                "email": "duplicate@example.com",
                "name": "First User",
                "role": "athlete",
            },
            {
                "user_id": "user456",
                "email": "duplicate@example.com",
                "name": "Second User",
                "role": "coach",
            },
        ]
        self.mock_table.query.return_value = {"Items": mock_users}

        # Call the method
        result = self.repository.get_user_by_email("duplicate@example.com")

        # Assert
        self.mock_table.query.assert_called_once_with(
            IndexName="email-index",
            KeyConditionExpression="email = :email",
            ExpressionAttributeValues={":email": "duplicate@example.com"},
            Limit=1,
        )
        # Should return only the first item
        self.assertEqual(result, mock_users[0])

    def test_create_user(self):
        """
        Test creating a new user
        """
        # Data to create
        user_data = {
            "user_id": "user123",
            "email": "user@example.com",
            "name": "Test User",
            "role": "athlete",
        }

        # Call the method
        result = self.repository.create_user(user_data)

        # Assert
        self.mock_table.put_item.assert_called_once_with(Item=user_data)
        self.assertEqual(result, user_data)

    def test_update_user(self):
        """
        Test updating a user
        """
        # Setup mock return value
        mock_updated_user = {
            "user_id": "user123",
            "email": "updated@example.com",  # Updated
            "name": "Updated User",  # Updated
            "role": "coach",  # Updated
        }
        self.mock_table.update_item.return_value = {"Attributes": mock_updated_user}

        # Update data
        update_data = {
            "email": "updated@example.com",
            "name": "Updated User",
            "role": "coach",
        }

        # Call the method
        result = self.repository.update_user("user123", update_data)

        # Assert
        self.mock_table.update_item.assert_called_once()

        # Verify the call arguments
        call_args = self.mock_table.update_item.call_args[1]
        self.assertEqual(call_args["Key"], {"user_id": "user123"})
        self.assertEqual(call_args["ReturnValues"], "ALL_NEW")

        # Verify UpdateExpression
        self.assertTrue(call_args["UpdateExpression"].startswith("set "))

        # Check that expression attribute names and values contain all expected keys
        for key in update_data.keys():
            self.assertIn(f"#{key}", call_args["ExpressionAttributeNames"])
            self.assertIn(f":{key}", call_args["ExpressionAttributeValues"])

        # Check returned data
        self.assertEqual(result, mock_updated_user)

    def test_update_user_single_attribute(self):
        """
        Test updating a single attribute of a user
        """
        # Setup mock return value
        mock_updated_user = {
            "user_id": "user123",
            "name": "Updated Name Only",  # Only name updated
        }
        self.mock_table.update_item.return_value = {"Attributes": mock_updated_user}

        # Update only name
        update_data = {"name": "Updated Name Only"}

        # Call the method
        result = self.repository.update_user("user123", update_data)

        # Assert
        self.mock_table.update_item.assert_called_once()

        # Verify the call arguments
        call_args = self.mock_table.update_item.call_args[1]

        # Check UpdateExpression is correct for single attribute
        self.assertEqual(call_args["UpdateExpression"], "set #name = :name")
        self.assertEqual(call_args["ExpressionAttributeNames"], {"#name": "name"})
        self.assertEqual(
            call_args["ExpressionAttributeValues"], {":name": "Updated Name Only"}
        )

        # Check returned data
        self.assertEqual(result, mock_updated_user)

    def test_update_user_no_attributes_returned(self):
        """
        Test update when DynamoDB doesn't return attributes
        """
        # Setup mock return value with no Attributes
        self.mock_table.update_item.return_value = {}

        # Update data
        update_data = {"name": "Updated Name"}

        # Call the method
        result = self.repository.update_user("user123", update_data)

        # Assert
        self.mock_table.update_item.assert_called_once()
        # Should return empty dict when no attributes
        self.assertEqual(result, {})


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
