import unittest
from unittest.mock import MagicMock, patch
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
        self.dt_now_patcher = patch("src.services.relationship_service.dt.datetime")
        self.dt_mock = self.dt_now_patcher.start()
        self.dt_mock.now.return_value.isoformat.return_value = "2025-03-13T12:00:00"

        # Initialize service with mocked repository
        with patch(
            "src.services.relationship_service.RelationshipRepository",
            return_value=self.relationship_repository_mock,
        ):
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
            coach_id="coach123", athlete_id="athlete456"
        )

        # Verify the repository was checked for existing relationship
        self.relationship_repository_mock.get_active_relationship.assert_called_once_with(
            "coach123", "athlete456"
        )

        # Verfiy a new relationship was created
        self.relationship_repository_mock.create_relationship.assert_called_once()

        # Verify the created relationship data
        relationship_dict = (
            self.relationship_repository_mock.create_relationship.call_args[0][0]
        )

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
            "created_at": "2025-03-01T09:00:00",
        }

        # Configure the mock to return the existing relationship
        self.relationship_repository_mock.get_active_relationship.return_value = (
            existing_relationship
        )

        # Call the service method
        result = self.relationship_service.create_relationship(
            coach_id="coach123", athlete_id="athlete456"
        )

        # Verify the repository was checked for existing relationship
        self.relationship_repository_mock.get_active_relationship.assert_called_once_with(
            "coach123", "athlete456"
        )

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
            "created_at": "2025-03-01T09:00:00",
        }

        # Configure the mock to return the pending relationship
        self.relationship_repository_mock.get_relationship.return_value = (
            pending_relationship
        )

        # Configure mock for update call
        self.relationship_repository_mock.update_relationship.return_value = {
            "Attributes": {"status": "active"}
        }

        # Mock the get_relationship method o return the updated relationship
        updated_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",
            "created_at": "2025-03-01T09:00:00",
        }

        # Setup the update_relationship method to return a Relationship object
        with patch.object(
            self.relationship_service, "update_relationship"
        ) as mock_update_relationship:
            mock_update_relationship.return_value = Relationship(**updated_relationship)

            # Call the service method
            result = self.relationship_service.accept_relationship("rel123")

            # Verify the relationship was retrieved
            self.relationship_repository_mock.get_relationship.assert_called_once_with(
                "rel123"
            )

            # Verify the update was called with correct parameters
            mock_update_relationship.assert_called_once_with(
                "rel123", {"status": "active"}
            )

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
        self.relationship_repository_mock.get_relationship.assert_called_once_with(
            "nonexistent-rel"
        )

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
            "created_at": "2025-03-01T09:00:00",
        }

        # Configure the mock to return the active relationship
        self.relationship_repository_mock.get_relationship.return_value = (
            active_relationship
        )

        # Call the service method
        result = self.relationship_service.accept_relationship("rel123")

        # Verify the repository was called
        self.relationship_repository_mock.get_relationship.assert_called_once_with(
            "rel123"
        )

        # Verify the update was not called
        self.relationship_repository_mock.update_relationship.assert_not_called()

        # Verify the result is None
        self.assertIsNone(result)

    def test_end_relationship_with_ttl(self):
        """
        Test ending an active relationship and setting TTL for cleanup
        """
        # Mock data for an active relationship
        active_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",
            "created_at": "2025-03-01T09:00:00",
        }

        # Configure the mock to return the active relationship
        self.relationship_repository_mock.get_relationship.return_value = (
            active_relationship
        )

        # Mock the updated relationship with TTL
        ended_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "ended",
            "created_at": "2025-03-01T09:00:00",
            "ttl": 1720958400,  # 60 days from end date
        }

        # Setup the update_relationship to return a Relationship object
        with patch.object(
            self.relationship_service, "update_relationship"
        ) as mock_update_relationship:
            mock_update_relationship.return_value = Relationship(**ended_relationship)

            # Call the service method
            result = self.relationship_service.end_relationship("rel123")

            # Verify the relationship was retrieved
            self.relationship_repository_mock.get_relationship.assert_called_once_with(
                "rel123"
            )

            # Verify the update was called with status and TTL
            mock_update_relationship.assert_called_once()
            call_args = mock_update_relationship.call_args[0]
            self.assertEqual(call_args[0], "rel123")
            self.assertEqual(call_args[1]["status"], "ended")
            self.assertIn("ttl", call_args[1])

            # Verify the returned object is the updated relationship
            self.assertIsInstance(result, Relationship)
            self.assertEqual(result.relationship_id, "rel123")
            self.assertEqual(result.status, "ended")
            self.assertEqual(result.ttl, 1720958400)

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
            "created_at": "2025-03-01T09:00:00",
        }

        # Configure mock to return the already ended relationship
        self.relationship_repository_mock.get_relationship.return_value = (
            ended_relationship
        )

        # Call the service method
        result = self.relationship_service.end_relationship("rel123")

        # Assert repository get_relationship was called
        self.relationship_repository_mock.get_relationship.assert_called_once_with(
            "rel123"
        )

        # Create a separate mock for update_relationship to verify it was NOT called
        with patch.object(
            self.relationship_service, "update_relationship"
        ) as mock_update_relationship:
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
                "created_at": "2025-03-01T09:00:00",
            },
            {
                "relationship_id": "rel2",
                "coach_id": "coach123",
                "athlete_id": "athlete2",
                "status": "pending",
                "created_at": "2025-03-02T10:00:00",
                "invitation_code": "ABC123",
                "ttl": 1678701600,
            },
            {
                "relationship_id": "rel3",
                "coach_id": "coach123",
                "athlete_id": "athlete3",
                "status": "ended",
                "created_at": "2025-03-03T08:00:00",
                "ttl": 1720958400,
            },
        ]

        # Configure the mock to return the relationships data
        self.relationship_repository_mock.get_relationships_for_coach.return_value = (
            relationships_data
        )

        # Call the service method
        result = self.relationship_service.get_relationships_for_coach("coach123")

        # Verify the repository was called
        self.relationship_repository_mock.get_relationships_for_coach.assert_called_once_with(
            "coach123", None
        )

        # Verify the result is a list of Relationship objects
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], Relationship)
        self.assertEqual(result[0].relationship_id, "rel1")
        self.assertEqual(result[1].relationship_id, "rel2")
        self.assertEqual(result[2].relationship_id, "rel3")

        # Verify TTL fields are preserved
        self.assertIsNone(result[0].ttl)  # Active relationship has no TTL
        self.assertEqual(result[1].ttl, 1678701600)  # Pending has TTL
        self.assertEqual(result[2].ttl, 1720958400)  # Ended has TTL

    def test_generate_invitation_code_with_ttl(self):
        """
        Test generating an invitation code with TTL for a coach
        """
        # Setup
        coach_id = "coach789"

        # Mock the RelationshipConfig values
        with patch(
            "src.services.relationship_service.RelationshipConfig"
        ) as mock_config:
            mock_config.INVITATION_CODE_TTL_HOURS = 24

            # patch dt.datetime so that now() returns mock_future
            with patch("src.services.relationship_service.dt.datetime") as dt_cls:
                mock_now = MagicMock()
                mock_future = MagicMock()
                # dt.datetime.now() → mock_now
                dt_cls.now.return_value = mock_now
                # mock_now + ANY → mock_future
                mock_now.__add__.return_value = mock_future
                # timestamp() on that future → our fixed epoch
                mock_future.timestamp.return_value = 1678701600

                # Call the method
                result = self.relationship_service.generate_invitation_code(coach_id)

        # Assert that repository was called
        self.relationship_repository_mock.create_relationship.assert_called_once()

        # Verify the created relationship data
        relationship_dict = (
            self.relationship_repository_mock.create_relationship.call_args[0][0]
        )

        self.assertEqual(relationship_dict["relationship_id"], "test-uuid")
        self.assertEqual(relationship_dict["coach_id"], coach_id)
        self.assertEqual(relationship_dict["invitation_code"], result.invitation_code)
        self.assertEqual(
            relationship_dict["ttl"], 1678701600
        )  # TTL field instead of expiration_time
        self.assertNotIn("athlete_id", relationship_dict)
        self.assertEqual(relationship_dict["status"], "pending")

        # Verify returned object
        self.assertIsInstance(result, Relationship)
        self.assertEqual(result.invitation_code, relationship_dict["invitation_code"])
        self.assertEqual(result.ttl, 1678701600)

    def test_validate_invitation_code_athlete_has_relationship(self):
        """
        Test validation fails when athlete already has an active relationship
        """
        # Setup
        invitation_code = "TESTCODE123"
        athlete_id = "athlete123"

        # Mock athlete already having an active relationship
        self.relationship_repository_mock.get_active_relationship_for_athlete.return_value = {
            "relationship_id": "existing-rel",
            "coach_id": "coach456",
            "athlete_id": athlete_id,
            "status": "active",
        }

        # Act & Assert exception
        with self.assertRaises(ValueError) as context:
            self.relationship_service.validate_invitation_code(
                invitation_code, athlete_id
            )

        # Verify error message
        self.assertIn(
            "Athlete already has an active coach relationship", str(context.exception)
        )

        # Verify repository called with correct parameters
        self.relationship_repository_mock.get_active_relationship_for_athlete.assert_called_once_with(
            athlete_id
        )

        # Verify code validation was not attempted
        self.relationship_repository_mock.get_relationship_by_code.assert_not_called()

    def test_validate_invitation_code_not_found(self):
        """
        Test validation fails when invitation code doesn't exist
        """
        # Setup
        invitation_code = "NONEXISTENT"
        athlete_id = "athlete123"

        # Mock athlete not having a relationship
        self.relationship_repository_mock.get_active_relationship_for_athlete.return_value = (
            None
        )

        # Mock invitation code not found
        self.relationship_repository_mock.get_relationship_by_code.return_value = None

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.relationship_service.validate_invitation_code(
                invitation_code, athlete_id
            )

        # Verify correct error code
        self.assertEqual(str(context.exception), "INVALID_CODE")

        # Verify repository methods called correctly
        self.relationship_repository_mock.get_active_relationship_for_athlete.assert_called_once_with(
            athlete_id
        )
        self.relationship_repository_mock.get_relationship_by_code.assert_called_once_with(
            invitation_code
        )

    def test_validate_invitation_code_expired(self):
        """
        Test validation fails when invitation code is expired
        """
        # Setup
        invitation_code = "EXPIRED"
        athlete_id = "athlete123"

        # Mock athlete not having a relationship
        self.relationship_repository_mock.get_active_relationship_for_athlete.return_value = (
            None
        )

        # Mock time.time() for consistent testing
        with patch("time.time", return_value=1678701600):  # current time
            # Mock invitation code found but expired
            self.relationship_repository_mock.get_relationship_by_code.return_value = {
                "relationship_id": "rel789",
                "coach_id": "coach456",
                "invitation_code": invitation_code,
                "ttl": 1678697000,  # earlier than current time
            }

            # Act & Assert
            with self.assertRaises(ValueError) as context:
                self.relationship_service.validate_invitation_code(
                    invitation_code, athlete_id
                )

        # Verify correct error code
        self.assertEqual(str(context.exception), "EXPIRED_CODE")

        # Verify code was found but no update attempted
        self.relationship_repository_mock.get_relationship_by_code.assert_called_once_with(
            invitation_code
        )

    def test_validate_invitation_code_success(self):
        """
        Test successful validation and acceptance of invitation code
        """
        # Setup
        invitation_code = "VALID123"
        athlete_id = "athlete123"
        relationship_id = "rel456"

        # Mock athlete not having a relationship
        self.relationship_repository_mock.get_active_relationship_for_athlete.return_value = (
            None
        )

        # Create mock for update_relationship method
        self.relationship_service.update_relationship = MagicMock()

        # Mock returned updated relationship
        updated_relationship = Relationship(
            relationship_id=relationship_id,
            coach_id="coach789",
            athlete_id=athlete_id,
            status="active",
        )
        self.relationship_service.update_relationship.return_value = (
            updated_relationship
        )

        # Mock current time for expiration check
        with patch("time.time", return_value=1678701600):  # current time
            # Mock invitation code found and valid
            self.relationship_repository_mock.get_relationship_by_code.return_value = {
                "relationship_id": relationship_id,
                "coach_id": "coach789",
                "invitation_code": invitation_code,
                "ttl": 1678705200,  # future timestamp
            }

            # Act
            result = self.relationship_service.validate_invitation_code(
                invitation_code, athlete_id
            )

        # Assert
        self.assertEqual(result, updated_relationship)

        # Verify correct update was attempted (TTL-based)
        expected_update = {
            "athlete_id": athlete_id,
            "status": "active",
            "invitation_code": None,
            "ttl": None,  # Remove TTL for active relationships
        }
        self.relationship_service.update_relationship.assert_called_once_with(
            relationship_id, expected_update
        )

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
            "created_at": "2025-03-01T09:00:00",
        }

        # Mock data for the updated relationship
        updated_relationship = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",  # Updated from ended to active
            "created_at": "2025-03-01T09:00:00",
        }

        # Configure mocks
        self.relationship_repository_mock.update_relationship.return_value = {
            "Attributes": {"status": "active"}
        }

        # First return the initial relationship, then the updated one
        self.relationship_repository_mock.get_relationship.side_effect = [
            initial_relationship,
            updated_relationship,
        ]

        # Relationship repository returns success
        self.relationship_repository_mock.update_relationship.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }

        # Verify initial status is "ended"
        initial_result = self.relationship_service.get_relationship("rel123")
        self.assertEqual(initial_result.status, "ended")

        # Data to update
        update_data = {"status": "active"}

        # Call the service method directly
        result = self.relationship_service.update_relationship("rel123", update_data)

        # Assert repository methods were called correctly
        self.relationship_repository_mock.update_relationship.assert_called_once_with(
            "rel123", update_data
        )

        # Assert get_relationship was called twice (once before update, and once after update)
        self.assertEqual(
            self.relationship_repository_mock.get_relationship.call_count, 2
        )

        # Assert the returned object has the updated status
        self.assertIsInstance(result, Relationship)
        self.assertEqual(result.status, "active")
        self.assertEqual(initial_result.status, "ended")

        # Assert other fields remain unchanged
        self.assertEqual(result.relationship_id, "rel123")
        self.assertEqual(result.coach_id, "coach456")
        self.assertEqual(result.athlete_id, "athlete789")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
