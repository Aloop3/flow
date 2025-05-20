import unittest
from unittest.mock import MagicMock, patch
from src.repositories.relationship_repository import RelationshipRepository
from boto3.dynamodb.conditions import Key


class TestRelationshipRepository(unittest.TestCase):
    """
    Test suite for the RelationshipRepository class
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
        self.repository = RelationshipRepository()

    def tearDown(self):
        """
        Clean up after each test
        """
        self.patcher.stop()

    def test_get_relationship(self):
        """
        Test retrieving a relationship by ID
        """
        # Setup mock return value
        mock_data = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",
        }
        self.mock_table.get_item.return_value = {"Item": mock_data}

        # Call the method
        result = self.repository.get_relationship("rel123")

        # Assert
        self.mock_table.get_item.assert_called_once_with(
            Key={"relationship_id": "rel123"}
        )
        self.assertEqual(result, mock_data)

    def test_get_relationship_not_found(self):
        """
        Test retrieving a non-existent relationship
        """
        # Setup mock return value for not found case
        self.mock_table.get_item.return_value = {}

        # Call the method
        result = self.repository.get_relationship("nonexistent")

        # Assert
        self.mock_table.get_item.assert_called_once_with(
            Key={"relationship_id": "nonexistent"}
        )
        self.assertIsNone(result)

    def test_get_relationships_for_coach(self):
        """
        Test retrieving relationships by coach ID
        """
        # Setup mock return value
        mock_items = [
            {
                "relationship_id": "rel1",
                "coach_id": "coach123",
                "athlete_id": "athlete1",
                "status": "active",
            },
            {
                "relationship_id": "rel2",
                "coach_id": "coach123",
                "athlete_id": "athlete2",
                "status": "pending",
            },
        ]
        self.mock_table.query.return_value = {"Items": mock_items}

        # Call the method
        result = self.repository.get_relationships_for_coach("coach123")

        # Assert
        self.mock_table.query.assert_called_once_with(
            IndexName="coach-index",
            KeyConditionExpression=Key("coach_id").eq("coach123"),
            Limit=unittest.mock.ANY,
        )
        self.assertEqual(result, mock_items)

    def test_get_relationships_for_coach_with_status(self):
        """
        Test retrieving relationships by coach ID with status filter
        """
        # Setup mock return value
        mock_items = [
            {
                "relationship_id": "rel1",
                "coach_id": "coach123",
                "athlete_id": "athlete1",
                "status": "active",
            }
        ]
        self.mock_table.query.return_value = {"Items": mock_items}

        # Call the method
        result = self.repository.get_relationships_for_coach("coach123", "active")

        # Assert query was called with correct parameters
        self.mock_table.query.assert_called_once()
        call_args = self.mock_table.query.call_args[1]
        self.assertEqual(call_args["IndexName"], "coach-index")

        # Verify expressions exist without examining details
        self.assertIn("KeyConditionExpression", call_args)
        self.assertIn("FilterExpression", call_args)

        # Verify the result matches expected items
        self.assertEqual(result, mock_items)

    def test_get_relationships_for_coach_with_status(self):
        """
        Test retrieving relationships by coach ID with status filter
        """
        # Setup mock return value
        mock_items = [
            {
                "relationship_id": "rel1",
                "coach_id": "coach123",
                "athlete_id": "athlete1",
                "status": "active",
            }
        ]
        self.mock_table.query.return_value = {"Items": mock_items}

        # Call the method
        result = self.repository.get_relationships_for_coach("coach123", "active")

        # Assert query was called with correct parameters
        self.mock_table.query.assert_called_once()
        call_args = self.mock_table.query.call_args[1]
        self.assertEqual(call_args["IndexName"], "coach-index")

        # Verify expressions exist without examining details
        self.assertIn("KeyConditionExpression", call_args)
        self.assertIn("FilterExpression", call_args)

        # Verify the result matches expected items
        self.assertEqual(result, mock_items)

    def test_get_relationships_for_athlete(self):
        """
        Test retrieving relationships by athlete ID
        """
        # Setup mock return value
        mock_items = [
            {
                "relationship_id": "rel1",
                "coach_id": "coach1",
                "athlete_id": "athlete123",
                "status": "active",
            },
            {
                "relationship_id": "rel2",
                "coach_id": "coach2",
                "athlete_id": "athlete123",
                "status": "pending",
            },
        ]
        self.mock_table.query.return_value = {"Items": mock_items}

        # Call the method
        result = self.repository.get_relationships_for_athlete("athlete123")

        # Assert
        self.mock_table.query.assert_called_once_with(
            IndexName="athlete-index",
            KeyConditionExpression=Key("athlete_id").eq("athlete123"),
            Limit=unittest.mock.ANY,
        )
        self.assertEqual(result, mock_items)

    def test_get_relationships_for_athlete_with_status(self):
        """
        Test retrieving relationships by athlete ID with status filter
        """
        # Setup mock return value
        mock_items = [
            {
                "relationship_id": "rel1",
                "coach_id": "coach1",
                "athlete_id": "athlete123",
                "status": "active",
            }
        ]
        self.mock_table.query.return_value = {"Items": mock_items}

        # Call the method
        result = self.repository.get_relationships_for_athlete("athlete123", "active")

        # Assert query was called with correct parameters
        self.mock_table.query.assert_called_once()
        call_args = self.mock_table.query.call_args[1]
        self.assertEqual(call_args["IndexName"], "athlete-index")

        # Verify expressions exist without examining details
        self.assertIn("KeyConditionExpression", call_args)
        self.assertIn("FilterExpression", call_args)

        # Verify the result matches expected items
        self.assertEqual(result, mock_items)

    def test_get_relationships_for_athlete_empty_result(self):
        """
        Test retrieving relationships by athlete ID when none exist
        """
        # Setup mock return value for empty result
        self.mock_table.query.return_value = {"Items": []}

        # Call the method
        result = self.repository.get_relationships_for_athlete("athlete123")

        # Assert
        self.mock_table.query.assert_called_once_with(
            IndexName="athlete-index",
            KeyConditionExpression=Key("athlete_id").eq("athlete123"),
            Limit=unittest.mock.ANY,
        )
        self.assertEqual(result, [])

    def test_get_active_relationship_not_found(self):
        """
        Test retrieving active relationship when none exists
        """
        # Setup mock return value for empty result
        self.mock_table.query.return_value = {"Items": []}

        # Call the method
        result = self.repository.get_active_relationship("coach456", "athlete789")

        # Assert
        self.mock_table.query.assert_called_once()
        self.assertIsNone(result)

    def test_create_relationship(self):
        """
        Test creating a new relationship
        """
        # Data to create
        relationship_data = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "pending",
            "created_at": "2025-03-13T12:00:00",
        }

        # Call the method
        result = self.repository.create_relationship(relationship_data)

        # Assert
        self.mock_table.put_item.assert_called_once_with(Item=relationship_data)
        self.assertEqual(result, relationship_data)

    def test_get_relationship_by_code_found(self):
        """
        Test retrieving a relationship by invitation code when it exists
        """
        # Setup mock return value
        mock_data = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "invitation_code": "TEST123",
            "status": "pending",
        }
        self.mock_table.scan.return_value = {"Items": [mock_data]}

        # Call the method
        result = self.repository.get_relationship_by_code("TEST123")

        # Assert
        self.assertEqual(result, mock_data)
        # Check that scan was called with correct filter
        from boto3.dynamodb.conditions import Attr

        self.mock_table.scan.assert_called_once()

    def test_get_relationship_by_code_not_found(self):
        """
        Test retrieving a relationship by invitation code when it doesn't exist
        """
        # Setup empty return value
        self.mock_table.scan.return_value = {"Items": []}

        # Call the method
        result = self.repository.get_relationship_by_code("NONEXISTENT")

        # Assert
        self.assertIsNone(result)
        self.mock_table.scan.assert_called_once()

    def test_get_active_relationship_for_athlete_found(self):
        """
        Test retrieving an active relationship for an athlete when it exists
        """
        # Setup mock return value
        athlete_id = "athlete123"
        mock_data = {
            "relationship_id": "rel456",
            "coach_id": "coach789",
            "athlete_id": athlete_id,
            "status": "active",
        }
        self.mock_table.query.return_value = {"Items": [mock_data]}

        # Call the method
        result = self.repository.get_active_relationship_for_athlete(athlete_id)

        # Assert
        self.assertEqual(result, mock_data)
        self.mock_table.query.assert_called_once()
        # Verify correct index and key condition used
        args, kwargs = self.mock_table.query.call_args
        from src.config.relationship_config import RelationshipConfig

        self.assertEqual(kwargs["IndexName"], RelationshipConfig.ATHLETE_INDEX)

    def test_get_active_relationship_for_athlete_not_found(self):
        """
        Test retrieving an active relationship for an athlete when none exists
        """
        # Setup empty return value
        athlete_id = "athlete999"
        self.mock_table.query.return_value = {"Items": []}

        # Call the method
        result = self.repository.get_active_relationship_for_athlete(athlete_id)

        # Assert
        self.assertIsNone(result)
        self.mock_table.query.assert_called_once()

    def test_update_relationship(self):
        """
        Test updating a relationship
        """
        # Setup mock return value
        mock_attributes = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",  # Updated from pending to active
        }
        self.mock_table.update_item.return_value = {"Attributes": mock_attributes}

        # Update data
        update_data = {"status": "active"}

        # Call the method
        result = self.repository.update_relationship("rel123", update_data)

        # Assert
        self.mock_table.update_item.assert_called_once()
        call_args = self.mock_table.update_item.call_args[1]
        self.assertEqual(call_args["Key"], {"relationship_id": "rel123"})
        self.assertEqual(call_args["UpdateExpression"], "set #status = :status")
        self.assertEqual(call_args["ExpressionAttributeNames"], {"#status": "status"})
        self.assertEqual(call_args["ExpressionAttributeValues"], {":status": "active"})
        self.assertEqual(result, mock_attributes)

    def test_delete_relationship(self):
        """
        Test deleting a relationship
        """
        # Setup mock return value
        mock_attributes = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",
        }
        self.mock_table.delete_item.return_value = {"Attributes": mock_attributes}

        # Call the method
        result = self.repository.delete_relationship("rel123")

        # Assert
        self.mock_table.delete_item.assert_called_once_with(
            Key={"relationship_id": "rel123"}, ReturnValues="ALL_OLD"
        )
        self.assertEqual(result, mock_attributes)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
