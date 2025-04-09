from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest
from src.models.week import Week
from src.services.week_service import WeekService


class TestWeekServiceParametrized(BaseTest):
    """Test suite for the WeekService class using parameterized tests."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create patchers for repositories
        self.week_repository_patcher = patch("src.services.week_service.WeekRepository")
        self.day_repository_patcher = patch("src.services.week_service.DayRepository")

        # Start patchers and get mocks
        self.mock_week_repository = self.week_repository_patcher.start()
        self.mock_day_repository = self.day_repository_patcher.start()

        # Create repository instances
        self.week_repository_instance = MagicMock()
        self.day_repository_instance = MagicMock()

        # Configure mocks to return instances
        self.mock_week_repository.return_value = self.week_repository_instance
        self.mock_day_repository.return_value = self.day_repository_instance

        # Create the service
        self.week_service = WeekService()

        # Create patcher for uuid
        self.uuid_patcher = patch("uuid.uuid4")
        self.mock_uuid = self.uuid_patcher.start()
        self.mock_uuid.return_value = "test-uuid"

    def tearDown(self):
        """Clean up after each test."""
        self.week_repository_patcher.stop()
        self.day_repository_patcher.stop()
        self.uuid_patcher.stop()

    def test_create_week_scenarios(self):
        """Test creating weeks with different parameters."""
        # Define test cases
        test_cases = [
            # block_id, week_number, notes, expected_result
            ("block123", 1, None, True),  # Basic week with no notes
            ("block123", 2, "Test notes", True),  # Week with notes
            ("block456", 10, "Last week", True),  # High week number
        ]

        for block_id, week_number, notes, expected_result in test_cases:
            with self.subTest(block_id=block_id, week_number=week_number, notes=notes):
                # Reset mock if needed
                self.week_repository_instance.create_week.reset_mock()

                # Call the method
                week = self.week_service.create_week(
                    block_id=block_id, week_number=week_number, notes=notes
                )

                # Assertions
                self.assertEqual(bool(week), expected_result)
                if expected_result:
                    self.assertIsInstance(week, Week)
                    self.assertEqual(week.week_id, "test-uuid")
                    self.assertEqual(week.block_id, block_id)
                    self.assertEqual(week.week_number, week_number)
                    # If notes were provided, they should match
                    if notes:
                        self.assertEqual(week.notes, notes)
                    else:
                        self.assertEqual(week.notes, "")  # Default is empty string

                    # Verify repository was called correctly
                    self.week_repository_instance.create_week.assert_called_once_with(
                        week.to_dict()
                    )

    def test_update_week_scenarios(self):
        """Test updating a week with different data combinations."""
        # Define test cases and expected results
        test_cases = [
            # update_data, original_notes, expected_notes
            (
                {"notes": "Updated notes"},
                "Original notes",
                "Updated notes",
            ),  # Update notes only
            (
                {"week_number": 5},
                "Original notes",
                "Original notes",
            ),  # Update week_number only, notes unchanged
            (
                {"notes": "New notes", "week_number": 10},
                "Original notes",
                "New notes",
            ),  # Update both
        ]

        for update_data, original_notes, expected_notes in test_cases:
            with self.subTest(update_data=update_data):
                # Reset mocks
                self.week_repository_instance.update_week.reset_mock()
                self.week_repository_instance.get_week.reset_mock()

                # Setup the test
                original_week_data = {
                    "week_id": "week123",
                    "block_id": "block456",
                    "week_number": 1,
                    "notes": original_notes,
                }

                # Create updated data by merging original with updates
                updated_week_data = {**original_week_data}  # Make a copy
                for key, value in update_data.items():
                    updated_week_data[key] = value

                # Configure mock behavior
                self.week_repository_instance.update_week.return_value = {
                    "ResponseMetadata": {"HTTPStatusCode": 200}
                }
                self.week_repository_instance.get_week.return_value = updated_week_data

                # Call the method
                result = self.week_service.update_week("week123", update_data)

                # Assertions
                self.assertIsNotNone(result)
                self.assertEqual(result.week_id, "week123")
                if "week_number" in update_data:
                    self.assertEqual(result.week_number, update_data["week_number"])
                else:
                    self.assertEqual(
                        result.week_number, original_week_data["week_number"]
                    )

                self.assertEqual(result.notes, expected_notes)

                # Verify repository was called correctly
                self.week_repository_instance.update_week.assert_called_once_with(
                    "week123", update_data
                )
                self.assertEqual(self.week_repository_instance.get_week.call_count, 1)

    def test_delete_week_scenarios(self):
        """Test deleting a week with different scenarios."""
        # Define test cases
        test_cases = [
            # days_deleted, delete_response, expected_result
            (
                3,
                {"ResponseMetadata": {"HTTPStatusCode": 200}},
                True,
            ),  # Successful delete with 3 days
            (
                0,
                {"ResponseMetadata": {"HTTPStatusCode": 200}},
                True,
            ),  # Successful delete with no days
            (2, None, False),  # Failed delete
        ]

        for days_deleted, delete_response, expected_result in test_cases:
            with self.subTest(
                days_deleted=days_deleted, delete_response=delete_response
            ):
                # Reset mocks
                self.day_repository_instance.delete_days_by_week.reset_mock()
                self.week_repository_instance.delete_week.reset_mock()

                # Configure mock behavior
                self.day_repository_instance.delete_days_by_week.return_value = (
                    days_deleted
                )
                self.week_repository_instance.delete_week.return_value = delete_response

                # Call the method
                result = self.week_service.delete_week("week123")

                # Assertions
                self.assertEqual(result, expected_result)

                # Verify repository calls
                self.day_repository_instance.delete_days_by_week.assert_called_once_with(
                    "week123"
                )
                self.week_repository_instance.delete_week.assert_called_once_with(
                    "week123"
                )
