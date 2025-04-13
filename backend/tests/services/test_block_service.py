import unittest
from unittest.mock import MagicMock, patch
from src.models.block import Block
from src.services.block_service import BlockService


class TestBlockService(unittest.TestCase):
    """
    Test suite for the BlockService
    """

    def setUp(self):
        """
        Set up test environment before each test method
        """
        self.block_repository_mock = MagicMock()
        self.week_repository_mock = MagicMock()
        self.week_service_mock = MagicMock()
        self.day_service_mock = MagicMock()

        # Create mock objects for week and day services to return
        self.mock_week = MagicMock()
        self.mock_week.week_id = "test-week-id"
        self.week_service_mock.create_week.return_value = self.mock_week

        self.mock_day = MagicMock()
        self.day_service_mock.create_day.return_value = self.mock_day

        # Create patcher for uuid4 to return predictable IDs
        self.uuid_patcher = patch("uuid.uuid4", return_value="test-uuid")
        self.uuid_mock = self.uuid_patcher.start()

        # Initialize service with mocked repositories
        with patch(
            "src.services.block_service.BlockRepository",
            return_value=self.block_repository_mock,
        ), patch(
            "src.services.block_service.WeekRepository",
            return_value=self.week_repository_mock,
        ):
            self.block_service = BlockService()
            self.block_service.week_service = self.week_service_mock
            self.block_service.day_service = self.day_service_mock

    def tearDown(self):
        """
        Clean up after each test method
        """
        self.uuid_patcher.stop()

    def test_get_block(self):
        """
        Test retrieving a block by ID
        """
        # Mock data that would be returned from the repository
        mock_block_data = {
            "block_id": "block123",
            "athlete_id": "athlete456",
            "title": "Test Block",
            "description": "Test Description",
            "start_date": "2025-03-01",
            "end_date": "2025-03-29",
            "status": "active",
            "coach_id": "coach789",
        }

        # Configure mock to return our test data
        self.block_repository_mock.get_block.return_value = mock_block_data

        # Call the service method
        result = self.block_service.get_block("block123")

        # Assert repository was called with correct ID
        self.block_repository_mock.get_block.assert_called_once_with("block123")

        # Assert the result is a Block instance with correct data
        self.assertIsInstance(result, Block)
        self.assertEqual(result.block_id, "block123")
        self.assertEqual(result.athlete_id, "athlete456")
        self.assertEqual(result.title, "Test Block")

    def test_get_block_not_found(self):
        """
        Test retrieving a non-existent block returns None
        """
        # Configure mock to return None (block not found)
        self.block_repository_mock.get_block.return_value = None

        # Call the service method
        result = self.block_service.get_block("nonexistent")

        # Assert repository was called with correct ID
        self.block_repository_mock.get_block.assert_called_once_with("nonexistent")

        # Assert the result is None
        self.assertIsNone(result)

    def test_get_blocks_for_athlete(self):
        """
        Test retrieving all blocks for an athlete
        """
        # Mock data that would be returned from the repository
        mock_blocks_data = [
            {
                "block_id": "block1",
                "athlete_id": "athlete123",
                "title": "Block 1",
                "description": "Description 1",
                "start_date": "2025-03-01",
                "end_date": "2025-03-29",
                "status": "active",
                "coach_id": "coach456",
            },
            {
                "block_id": "block2",
                "athlete_id": "athlete123",
                "title": "Block 2",
                "description": "Description 2",
                "start_date": "2025-04-02",
                "end_date": "2025-05-02",
                "status": "draft",
                "coach_id": "coach456",
            },
        ]

        # Configure mock to return our test data
        self.block_repository_mock.get_blocks_by_athlete.return_value = mock_blocks_data

        # Call the service method
        result = self.block_service.get_blocks_for_athlete("athlete123")

        # Assert repository was called with correct athlete ID
        self.block_repository_mock.get_blocks_by_athlete.assert_called_once_with(
            "athlete123"
        )

        # Assert the result is a list of Block instances with correct data
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Block)
        self.assertEqual(result[0].block_id, "block1")
        self.assertEqual(result[1].block_id, "block2")

    def test_create_block(self):
        """
        Test creating a new block
        """
        # Reset the mock call counts
        self.week_service_mock.create_week.reset_mock()
        self.day_service_mock.create_day.reset_mock()
        # Call the service method
        result = self.block_service.create_block(
            athlete_id="athlete123",
            title="New Block",
            description="New Description",
            start_date="2025-03-01",
            end_date="2025-03-29",
            coach_id="coach456",
            status="draft",
        )

        # Assert the UUID function was called
        self.uuid_mock.assert_called()

        # Assert repository create method was called with correct data
        expected_block_dict = {
            "block_id": "test-uuid",
            "athlete_id": "athlete123",
            "title": "New Block",
            "description": "New Description",
            "start_date": "2025-03-01",
            "end_date": "2025-03-29",
            "coach_id": "coach456",
            "status": "draft",
            "number_of_weeks": 4,
        }

        self.block_repository_mock.create_block.assert_called_once()
        actual_arg = self.block_repository_mock.create_block.call_args[0][0]

        # Check that all keys match the expected values
        for key, value in expected_block_dict.items():
            self.assertEqual(actual_arg[key], value)

        # Assert the returned object is a Block with correct data
        self.assertIsInstance(result, Block)
        self.assertEqual(result.block_id, "test-uuid")
        self.assertEqual(result.athlete_id, "athlete123")
        self.assertEqual(result.title, "New Block")
        self.assertEqual(result.number_of_weeks, 4)

        # Verify the week_service.create_week was called for each week
        self.assertEqual(self.week_service_mock.create_week.call_count, 4)

        # Verify day_service.create_day was called for each day (4 weeks * 7 days)
        self.assertEqual(self.day_service_mock.create_day.call_count, 28)

    def test_create_block_without_coach(self):
        """
        Test creating a new block without a coach
        """
        # Reset the mock call counts
        self.week_service_mock.create_week.reset_mock()
        self.day_service_mock.create_day.reset_mock()

        # Call the service method
        result = self.block_service.create_block(
            athlete_id="athlete123",
            title="Self-Coached Block",
            description="No coach needed",
            start_date="2025-03-01",
            end_date="2025-03-29",
            status="active",
            number_of_weeks=4,
        )

        # Assert repository create method was called with correct data
        self.block_repository_mock.create_block.assert_called_once()
        actual_arg = self.block_repository_mock.create_block.call_args[0][0]

        # Check coach_id is None
        self.assertEqual(actual_arg["coach_id"], None)
        self.assertEqual(actual_arg["athlete_id"], "athlete123")

        # Assert other data is correct
        self.assertEqual(actual_arg["title"], "Self-Coached Block")
        self.assertEqual(actual_arg["status"], "active")
        self.assertEqual(actual_arg["number_of_weeks"], 4)

        # Verify the week_service.create_week was called for each week
        self.assertEqual(self.week_service_mock.create_week.call_count, 4)

        # Verify day_service.create_day was called for each day (4 weeks * 7 days)
        self.assertEqual(self.day_service_mock.create_day.call_count, 28)

    def test_delete_block(self):
        """
        Test deleting a block
        """
        # Configure mock to return a successful response
        self.block_repository_mock.delete_block.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }

        # Call the service method
        success_result = self.block_service.delete_block("block123")

        # Assert repository was called with correct ID
        self.block_repository_mock.delete_block.assert_called_once_with("block123")

        # Assert the result is True (successful deletion)
        self.assertTrue(success_result)

        # Test handling of an exception
        self.block_repository_mock.delete_block.side_effect = Exception(
            "Deletion failed"
        )
        delete_result = self.block_service.delete_block("block123")

        # Assert result is False due to the exception
        self.assertFalse(delete_result)

    def test_update_block(self):
        """
        Test updating a block with new information
        """
        # Mock initial block data
        initial_block_data = {
            "block_id": "block123",
            "athlete_id": "athlete456",
            "title": "Old Title",
            "description": "Old Description",
            "start_date": "2025-03-01",
            "end_date": "2025-03-29",
            "status": "draft",
            "coach_id": "coach789",
            "number_of_weeks": 4,
        }

        # Mock updated block data
        updated_block_data = {
            "block_id": "block123",
            "athlete_id": "athlete456",
            "title": "New Title",
            "description": "Updated Description",
            "start_date": "2025-03-01",
            "end_date": "2025-03-29",
            "status": "active",
            "coach_id": "coach789",
            "number_of_weeks": 6,
        }

        # Configure mocks
        self.block_repository_mock.update_block.return_value = {
            "Attributes": {"status": "active"}
        }

        # Configure mock to return the updated block data when get_block is called
        self.block_repository_mock.get_block.return_value = updated_block_data

        # Update data to send
        update_data = {
            "title": "New Title",
            "description": "Updated Description",
            "status": "active",
            "number_of_weeks": 6,
        }

        # Call the service method
        result = self.block_service.update_block("block123", update_data)

        # Assert repository methods were called correctly
        self.block_repository_mock.update_block.assert_called_once_with(
            "block123", update_data
        )
        self.assertGreaterEqual(self.block_repository_mock.get_block.call_count, 1)

        # Assert the returned object has the updated values
        self.assertIsInstance(result, Block)
        self.assertEqual(result.title, "New Title")
        self.assertEqual(result.description, "Updated Description")
        self.assertEqual(result.status, "active")
        self.assertEqual(result.number_of_weeks, 6)

        # Assert unchanged values remain the same
        self.assertEqual(result.athlete_id, "athlete456")
        self.assertEqual(result.start_date, "2025-03-01")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
