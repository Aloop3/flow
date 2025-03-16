import unittest
from unittest.mock import MagicMock, patch
import uuid
import datetime as dt
from src.models.relationship import Relationship
from src.services.relationship_service import RelationshipService

class TestRelationshipService(unittest.TestCase):
    """
    Test suite for the RelationshipService
    """

    def setUp(self):
        """
        Set up the test environment
        """
        self.relationship_repository_mock = MagicMock()

        # Create patcher for uuid4 to return predictable IDs
        self.uuid_patcher = patch("uuid.uuid4", return_value="test-uuid")
        self.uuid_mock = self.uuid_patcher.start()

        # Create patcher for datetime.now to return predictable timestamps
        self.dt_now_patcher = patch("datetime.datetime")
        self.dt_mock = self.dt_now_patcher.start()
        self.dt_mock.now.return_value.isoformat.return_value = "2025-03-13T12:00:00"

        # Initialize service with mocked repository
        with patch("src.services.relationship_service.RelationshipRepository", return_value=self.relationship_repository_mock):
            self.relationship_service = RelationshipService()
        
    def tearDown(self):
        """
        Clean up after each test
        """
        self.uuid_patcher.stop()
        self.dt_now_patcher.stop()
    
    def test_create_new_relationship(self):
        """
        Test creating a new coach-athlete relationship
        """
        # Configure mock to return None (no existing relationship)
        self.relationship_repository_mock.get_active_relationship.return_value = None

        # Call the service method
        result = self.relationship_service.create_relationship(
            coach_id="coach123",
            athlete_id="athlete456"
        )

        # Verify the repository was checked for existing relationship
        self.relationship_repository_mock.get_active_relationship.assert_called_once_with("coach123", "athlete456")

        # Verfiy a new relationship was created
        self.relationship_repository_mock.create_relationship.assert_called_once()

        # Verify the created relationship data
        relationship_dict = self.relationship_repository_mock.create_relationship.call_args[0][0]
        
        self.assertEqual(relationship_dict["relationship_id"], "test-uuid")
        self.assertEqual(relationship_dict["coach_id"], "coach123")
        self.assertEqual(relationship_dict["athlete_id"], "athlete456")
        self.assertEqual(relationship_dict["status"], "pending")
        self.assertEqual(relationship_dict["created_at"], "2025-03-13T12:00:00")

        # Verify the returned object
        self.assertIsInstance(result, Relationship)
        self.assertEqual(result.relationship_id, "test-uuid")
        self.assertEqual(result.status, "pending")

    def test_avoid_duplicate_relationship(self):
        """
        Test that craeting a relationship does not duplicate active ones
        """
        # Mock data for existing relationship
        existing_relationship = {
            "relationship_id": "rel789",
            "coach_id": "coach123",
            "athlete_id": "athlete456",
            "status": "active",
            "created_at": "2025-03-01T09:00:00"
        }

        # Configure the mock to return the existing relationship
        self.relationship_repository_mock.get_active_relationship.return_value = existing_relationship

        # Call the service method
        result = self.relationship_service.create_relationship(coach_id="coach123", athlete_id="athlete456")

        # Verify the repository was checked for existing relationship
        self.relationship_repository_mock.get_active_relationship.assert_called_once_with("coach123", "athlete456")

        # Verify no new relationship was created
        self.relationship_repository_mock.create_relationship.assert_not_called()

        # Verify the returned object is the existing relationship
        self.assertIsInstance(result, Relationship)
        self.assertEqual(result.relationship_id, "rel789")
        self.assertEqual(result.status, "active")
        self.assertEqual(result.created_at, "2025-03-01T09:00:00")

    def test_accept_relationship(self):
        """
        Test accepting a pending relationship
        """
        # Mock data for pending relationship
        pending_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "pending",
            "created_at": "2025-03-01T09:00:00"
        }

        # Configure the mock to return the pending relationship
        self.relationship_repository_mock.get_relationship.return_value = pending_relationship

        # Configure mock for update call
        self.relationship_repository_mock.update_relationship.return_value = {
            "Attributes": {
                "status": "active"
            }
        }

        # Mock the get_relationship method o return the updated relationship
        updated_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",
            "created_at": "2025-03-01T09:00:00"
        }

        # Setup the update_relationship method to return a Relationship object
        with patch.object(self.relationship_service, "update_relationship") as mock_update_relationship:
            mock_update_relationship.return_value = Relationship(**updated_relationship)
        
            # Call the service method
            result = self.relationship_service.accept_relationship("rel123")

            # Verify the relationship was retrieved
            self.relationship_repository_mock.get_relationship.assert_called_once_with("rel123")

            # Verify the update was called with correct parameters
            mock_update_relationship.assert_called_once_with("rel123", {"status": "active"})

            # Verify the returned object is the updated relationship
            self.assertIsInstance(result, Relationship)
            self.assertEqual(result.relationship_id, "rel123")
            self.assertEqual(result.status, "active")
    
    def test_accept_nonexistent_relationship(self):
        """
        Test accepting a relationship that doesn't exist
        """
        # Configure the mock to return None
        self.relationship_repository_mock.get_relationship.return_value = None

        # Call the service method
        result = self.relationship_service.accept_relationship("nonexistent-rel")

        # Verify the repository was called
        self.relationship_repository_mock.get_relationship.assert_called_once_with("nonexistent-rel")
        
        # Verify update was not called
        self.relationship_repository_mock.update_relationship.assert_not_called()

        # Verifty the result is None
        self.assertIsNone(result)
    
    def test_accept_non_pending_relationship(self):
        """
        Test accepting a relationship that is not in pending status
        """
        # Mock data for an active relationship
        active_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",  # Already active
            "created_at": "2025-03-01T09:00:00"
        }

        # Configure the mock to return the active relationship
        self.relationship_repository_mock.get_relationship.return_value = active_relationship

        # Call the service method
        result = self.relationship_service.accept_relationship("rel123")

        # Verify the repository was called
        self.relationship_repository_mock.get_relationship.assert_called_once_with("rel123")

        # Verify the update was not called
        self.relationship_repository_mock.update_relationship.assert_not_called()

        # Verify the result is None
        self.assertIsNone(result)
    
    def test_end_relationship(self):
        """
        Test ending an active relationship
        """
        # Mock data for an active relationship
        active_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",
            "created_at": "2025-03-01T09:00:00"
        }

        # Configure the mock to return the active relationship
        self.relationship_repository_mock.get_relationship.return_value = active_relationship

        # Mock the updated relationship
        ended_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "ended",
            "created_at": "2025-03-12T09:00:00"
        }

        # Setup the update_relationship to return a Relationship object
        with patch.object(self.relationship_service, "update_relationship") as mock_update_relationship:
            mock_update_relationship.return_value = Relationship(**ended_relationship)

            # Call the service method
            result = self.relationship_service.end_relationship("rel123")

            # Verify the relationship was retrieved
            self.relationship_repository_mock.get_relationship.assert_called_once_with("rel123")

            # Verify the update was called with correct parameters
            mock_update_relationship.assert_called_once_with("rel123", {"status": "ended"})

            # Verify the returned object is the updated relationship
            self.assertIsInstance(result, Relationship)
            self.assertEqual(result.relationship_id, "rel123")
            self.assertEqual(result.status, "ended")

    def test_end_relationship_already_ended(self):
        """
        Test ending a relationship that has "ended" status
        """
        # Mock data for an already ended relationship
        ended_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "ended",  # Already ended
            "created_at": "2025-03-01T09:00:00"
        }
        
        # Configure mock to return the already ended relationship
        self.relationship_repository_mock.get_relationship.return_value = ended_relationship
        
        # Call the service method
        result = self.relationship_service.end_relationship("rel123")
        
        # Assert repository get_relationship was called
        self.relationship_repository_mock.get_relationship.assert_called_once_with("rel123")
        
        # Create a separate mock for update_relationship to verify it was NOT called
        with patch.object(self.relationship_service, 'update_relationship') as mock_update_relationship:
            result = self.relationship_service.end_relationship("rel123")
            mock_update_relationship.assert_not_called()
        
        # Assert the result is None (can't end an already ended relationship)
        self.assertIsNone(result)
    
    def test_get_relationships_for_coach(self):
        """
        Test retrieving all relationships for a coach
        """
        # Mock data for relationships
        relationships_data = [
            {
                "relationship_id": "rel1",
                "coach_id": "coach123",
                "athlete_id": "athlete1",
                "status": "active",
                "created_at": "2025-03-01T09:00:00"
            },
            {
                "relationship_id": "rel2",
                "coach_id": "coach123",
                "athlete_id": "athlete2",
                "status": "pending",
                "created_at": "2025-03-02T10:00:00"
            },
            {
                "relationship_id": "rel3",
                "coach_id": "coach123",
                "athlete_id": "athlete3",
                "status": "pending",
                "created_at": "2025-03-03T08:00:00"
            }
        ]

        # Configure the mock to return the relationships data
        self.relationship_repository_mock.get_relationships_for_coach.return_value = relationships_data

        # Call the service method
        result = self.relationship_service.get_relationships_for_coach("coach123")
        
        # Verify the repository was called
        self.relationship_repository_mock.get_relationships_for_coach.assert_called_once_with("coach123", None)

        # Verify the result is a list of Relationship objects
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], Relationship)
        self.assertEqual(result[0].relationship_id, "rel1")
        self.assertEqual(result[1].relationship_id, "rel2")
        self.assertEqual(result[2].relationship_id, "rel3")
    
    def test_update_relationship(self):
        """
        Test the update_relationship method
        """
        # Mock data for the initial relationship
        initial_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "ended",
            "created_at": "2025-03-01T09:00:00"
        }
        
        # Mock data for the updated relationship
        updated_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",  # Updated from ended to active
            "created_at": "2025-03-01T09:00:00"
        }
        
        # Configure mocks
        self.relationship_repository_mock.update_relationship.return_value = {"Attributes": {"status": "active"}}
        
        # First return the initial relationship, then the updated one
        self.relationship_repository_mock.get_relationship.side_effect = [initial_relationship, updated_relationship]

        # Relationship repository returns success
        self.relationship_repository_mock.update_relationship.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Verify initial status is "pending"
        initial_result = self.relationship_service.get_relationship("rel123")
        self.assertEqual(initial_result.status, "ended")

        # Data to update
        update_data = {
            "status": "active"
        }
        
        # Call the service method directly
        result = self.relationship_service.update_relationship("rel123", update_data)
        
        # Assert repository methods were called correctly
        self.relationship_repository_mock.update_relationship.assert_called_once_with("rel123", update_data)

        # Assert get_relationship was called twice (once before update, and once after update)
        self.assertEqual(self.relationship_repository_mock.get_relationship.call_count, 2)

        
        # Assert the returned object has the updated status
        self.assertIsInstance(result, Relationship)
        self.assertEqual(result.status, "active")
        self.assertEqual(initial_result.status, "ended")
        
        # Assert other fields remain unchanged
        self.assertEqual(result.relationship_id, "rel123")
        self.assertEqual(result.coach_id, "coach456")
        self.assertEqual(result.athlete_id, "athlete789")


if __name__ == '__main__': # pragma: no cover
    unittest.main()