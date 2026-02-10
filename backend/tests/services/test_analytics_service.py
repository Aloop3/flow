import unittest
from unittest.mock import MagicMock, patch
from src.services.analytics_service import AnalyticsService
import datetime as dt


class TestAnalyticsService(unittest.TestCase):
    """
    Test suite for the AnalyticsService class using new sets_data structure
    """

    def setUp(self):
        """
        Set up test environment before each test method
        Patches uuid.uuid4 to return consistent test values and initializes mocked repositories
        """
        # Patch uuid to return consistent test values
        with patch("uuid.uuid4", return_value="test-uuid"):
            # Mock all repository dependencies
            self.exercise_repository_mock = MagicMock()
            self.block_repository_mock = MagicMock()
            self.week_repository_mock = MagicMock()
            self.day_repository_mock = MagicMock()

            # Initialize service with mocked repositories
            with patch(
                "src.services.analytics_service.ExerciseRepository",
                return_value=self.exercise_repository_mock,
            ), patch(
                "src.services.analytics_service.BlockRepository",
                return_value=self.block_repository_mock,
            ), patch(
                "src.services.analytics_service.WeekRepository",
                return_value=self.week_repository_mock,
            ), patch(
                "src.services.analytics_service.DayRepository",
                return_value=self.day_repository_mock,
            ):
                self.analytics_service = AnalyticsService()

    def test_calculate_exercise_volume_with_completed_sets(self):
        """
        Test _calculate_exercise_volume helper method with completed sets_data
        Should sum volume from all completed sets: Σ(reps × weight) for completed sets
        """
        exercise = {
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                {"set_number": 2, "reps": 5, "weight": 105, "completed": True},
                {
                    "set_number": 3,
                    "reps": 3,
                    "weight": 110,
                    "completed": False,
                },  # Not completed
            ]
        }

        volume = self.analytics_service._calculate_exercise_volume(exercise)

        # Only completed sets: (5*100) + (5*105) = 500 + 525 = 1025
        expected_volume = 1025.0
        self.assertEqual(volume, expected_volume)

    def test_calculate_exercise_volume_no_sets_data(self):
        """
        Test _calculate_exercise_volume with missing or empty sets_data
        Should return 0.0 when no sets_data available
        """
        exercise_no_sets = {"sets_data": []}
        exercise_missing_sets = {}

        volume_no_sets = self.analytics_service._calculate_exercise_volume(
            exercise_no_sets
        )
        volume_missing_sets = self.analytics_service._calculate_exercise_volume(
            exercise_missing_sets
        )

        self.assertEqual(volume_no_sets, 0.0)
        self.assertEqual(volume_missing_sets, 0.0)

    def test_is_exercise_analytics_complete_all_conditions_met(self):
        """
        Test _is_exercise_analytics_complete when all conditions are met
        Exercise status = completed, workout status = completed, all sets completed
        """
        exercise = {
            "status": "completed",
            "workout_status": "completed",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                {"set_number": 2, "reps": 5, "weight": 105, "completed": True},
            ],
        }

        is_complete = self.analytics_service._is_exercise_analytics_complete(exercise)
        self.assertTrue(is_complete)

    def test_is_exercise_analytics_complete_incomplete_exercise(self):
        """
        Test _is_exercise_analytics_complete with incomplete exercise status
        Should return True - exercise status is no longer checked, only completed sets matter
        """
        exercise = {
            "status": "in_progress",
            "workout_status": "completed",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
            ],
        }

        is_complete = self.analytics_service._is_exercise_analytics_complete(exercise)
        self.assertTrue(is_complete)

    def test_is_exercise_analytics_complete_incomplete_workout(self):
        """
        Test _is_exercise_analytics_complete with incomplete workout status
        Should return True - workout status is no longer checked, only completed sets matter
        """
        exercise = {
            "status": "completed",
            "workout_status": "in_progress",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
            ],
        }

        is_complete = self.analytics_service._is_exercise_analytics_complete(exercise)
        self.assertTrue(is_complete)

    def test_is_exercise_analytics_complete_no_completed_sets(self):
        """
        Test _is_exercise_analytics_complete when no sets are completed
        Should return False when no sets have completed: True
        """
        exercise = {
            "status": "completed",
            "workout_status": "completed",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 100, "completed": False},
                {"set_number": 2, "reps": 5, "weight": 105, "completed": False},
            ],
        }

        is_complete = self.analytics_service._is_exercise_analytics_complete(exercise)
        self.assertFalse(is_complete)

    def test_is_exercise_analytics_complete_incomplete_sets(self):
        """
        Test _is_exercise_analytics_complete with some incomplete sets
        Should return True when at least one set is completed (changed from requiring all sets)
        """
        exercise = {
            "status": "completed",
            "workout_status": "completed",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                {
                    "set_number": 2,
                    "reps": 5,
                    "weight": 105,
                    "completed": False,
                },  # Not completed
            ],
        }

        is_complete = self.analytics_service._is_exercise_analytics_complete(exercise)
        self.assertTrue(is_complete)  # Should be True - at least one set completed

    def test_get_max_weight_from_exercise_completed_sets(self):
        """
        Test _get_max_weight_from_exercise with completed sets
        Should return the highest weight from completed sets only
        """
        exercise = {
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                {
                    "set_number": 2,
                    "reps": 3,
                    "weight": 120,
                    "completed": True,
                },  # Max weight
                {
                    "set_number": 3,
                    "reps": 1,
                    "weight": 150,
                    "completed": False,
                },  # Higher but not completed
            ]
        }

        max_weight = self.analytics_service._get_max_weight_from_exercise(exercise)

        # Should return 120, not 150 (since 150 is not completed)
        expected_max_weight = 120.0
        self.assertEqual(max_weight, expected_max_weight)

    def test_get_max_weight_history_success(self):
        """
        Test get_max_weight_history with valid exercise data using new structure
        Should group by date and return maximum weight per date from completed exercises
        """
        # Mock exercises with sets_data structure
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "exercise_type": "squat",
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                    {
                        "set_number": 2,
                        "reps": 5,
                        "weight": 105,
                        "completed": True,
                    },  # Max for this exercise
                ],
            },
            {
                "exercise_id": "ex2",
                "exercise_type": "squat",
                "status": "completed",
                "workout_date": "2024-01-01",  # Same date
                "workout_status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 110,
                        "completed": True,
                    },  # Max for the date
                ],
            },
            {
                "exercise_id": "ex3",
                "exercise_type": "squat",
                "status": "completed",
                "workout_date": "2024-01-08",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 115, "completed": True},
                ],
            },
        ]

        # Configure mock to return test data
        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        # Call the service method
        result = self.analytics_service.get_max_weight_history("athlete123", "squat")

        # Assert repository was called with correct parameters (NO exercise_type)
        self.exercise_repository_mock.get_exercises_with_workout_context.assert_called_once_with(
            athlete_id="athlete123"
        )

        # Assert the result is correctly processed
        # Date 2024-01-01: max(105, 110) = 110
        # Date 2024-01-08: 115
        expected_result = [
            {"date": "2024-01-01", "max_weight": 110},
            {"date": "2024-01-08", "max_weight": 115},
        ]
        self.assertEqual(result, expected_result)

    def test_get_max_weight_history_filters_incomplete_exercises(self):
        """
        Test that max weight history only requires at least one completed set
        Exercise status and workout status are no longer checked
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "exercise_type": "squat",
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                ],
            },
            {
                "exercise_id": "ex2",
                "exercise_type": "squat",
                "status": "in_progress",  # Not completed
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 200, "completed": True},
                ],
            },
            {
                "exercise_id": "ex3",
                "exercise_type": "squat",
                "status": "completed",
                "workout_date": "2024-01-02",
                "workout_status": "in_progress",  # Workout not completed
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 150, "completed": True},
                ],
            },
            {
                "exercise_id": "ex4",
                "exercise_type": "squat",
                "status": "completed",
                "workout_date": "2024-01-03",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 120, "completed": True},
                    {
                        "set_number": 2,
                        "reps": 5,
                        "weight": 180,
                        "completed": False,
                    },  # Mixed completion
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        result = self.analytics_service.get_max_weight_history("athlete123", "squat")

        # All exercises with at least one completed set are included (ex1, ex2, ex3, ex4)
        # ex1: date 2024-01-01, weight 100; ex2: date 2024-01-01, weight 200
        # ex3: date 2024-01-02, weight 150; ex4: date 2024-01-03, weight 120 (only completed set)
        expected_result = [
            {"date": "2024-01-01", "max_weight": 200},  # max(100, 200)
            {"date": "2024-01-02", "max_weight": 150},
            {"date": "2024-01-03", "max_weight": 120},
        ]
        self.assertEqual(result, expected_result)

    def test_calculate_volume_weekly(self):
        """
        Test calculate_volume for weekly time period using new sets_data structure
        Should sum volume from all completed sets within the time period
        """
        # Mock exercises with sets_data structure
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "status": "completed",
                "workout_date": "2024-01-02",
                "workout_status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 100,
                        "completed": True,
                    },  # 500
                    {
                        "set_number": 2,
                        "reps": 5,
                        "weight": 105,
                        "completed": True,
                    },  # 525
                    {
                        "set_number": 3,
                        "reps": 3,
                        "weight": 110,
                        "completed": False,
                    },  # Not counted
                ],
            },
            {
                "exercise_id": "ex2",
                "status": "completed",
                "workout_date": "2024-01-04",
                "workout_status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 8,
                        "weight": 80,
                        "completed": True,
                    },  # 640
                ],
            },
        ]

        # Configure mock
        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        # Call the service method with proper datetime mocking
        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_now = dt.datetime(2024, 1, 8)
            mock_dt.datetime.now.return_value = mock_now
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.calculate_volume("athlete123", "week")

        # Assert repository was called with correct start date
        expected_start_date = "2024-01-01"  # 2024-01-08 - 7 days
        self.exercise_repository_mock.get_exercises_with_workout_context.assert_called_once_with(
            athlete_id="athlete123", start_date=expected_start_date
        )

        # Assert volume calculations
        # Day 2024-01-02: (5*100) + (5*105) = 500 + 525 = 1025
        # Day 2024-01-04: (8*80) = 640
        expected_result = [
            {"date": "2024-01-02", "volume": 1025},
            {"date": "2024-01-04", "volume": 640},
        ]
        self.assertEqual(result, expected_result)

    def test_calculate_volume_only_counts_analytics_complete_exercises(self):
        """
        Test that volume calculation only requires at least one completed set
        Exercise status and workout status are no longer checked
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 100,
                        "completed": True,
                    },  # Valid: 500
                ],
            },
            {
                "exercise_id": "ex2",
                "status": "in_progress",  # Not completed
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 100,
                        "completed": True,
                    },  # Should be ignored
                ],
            },
            {
                "exercise_id": "ex3",
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 100,
                        "completed": True,
                    },  # Valid: 500
                    {
                        "set_number": 2,
                        "reps": 5,
                        "weight": 100,
                        "completed": False,
                    },  # Incomplete but exercise still counts
                ],
            },
            {
                "exercise_id": "ex4",
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 100,
                        "completed": False,
                    },  # No completed sets
                    {
                        "set_number": 2,
                        "reps": 5,
                        "weight": 100,
                        "completed": False,
                    },  # Exercise should be filtered out
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 1, 8)
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.calculate_volume("athlete123", "week")

        # ex1 (500) + ex2 (500, now included - exercise status no longer checked)
        # + ex3 (500 from completed set) = 1500
        # ex4 is filtered out (no completed sets)
        expected_result = [{"date": "2024-01-01", "volume": 1500}]
        self.assertEqual(result, expected_result)

    def test_get_exercise_frequency_success(self):
        """
        Test get_exercise_frequency with analytics-complete exercises
        Should count unique training days and total completed sets
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "exercise_type": "squat",  # Add exercise_type for filtering
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                    {"set_number": 2, "reps": 5, "weight": 105, "completed": True},
                    {
                        "set_number": 3,
                        "reps": 3,
                        "weight": 110,
                        "completed": False,
                    },  # Not counted
                ],
            },
            {
                "exercise_id": "ex2",
                "exercise_type": "squat",  # Add exercise_type for filtering
                "status": "completed",
                "workout_date": "2024-01-01",  # Same day
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 8, "weight": 80, "completed": True},
                ],
            },
            {
                "exercise_id": "ex3",
                "exercise_type": "squat",  # Add exercise_type for filtering
                "status": "completed",
                "workout_date": "2024-01-08",  # Different day
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 120, "completed": True},
                    {"set_number": 2, "reps": 5, "weight": 125, "completed": True},
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_now = dt.datetime(2024, 1, 31)
            mock_dt.datetime.now.return_value = mock_now
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.get_exercise_frequency(
                "athlete123", "squat", "month"
            )

        # Assert repository was called with correct parameters (NO exercise_type)
        expected_start_date = "2024-01-01"  # 30 days ago
        self.exercise_repository_mock.get_exercises_with_workout_context.assert_called_once_with(
            athlete_id="athlete123",
            start_date=expected_start_date,
        )

        # Assert calculations
        # Unique training days: 2024-01-01, 2024-01-08 = 2 days
        # Total completed sets: 2 + 1 + 2 = 5 sets
        # Frequency per week: 2 days / (30 days / 7) = 2 / 4.29 ≈ 0.47
        expected_result = {
            "exercise_type": "squat",
            "time_period": "month",
            "training_days": 2,
            "total_sets": 5,
            "frequency_per_week": 0.47,
            "period_days": 30,
        }
        self.assertEqual(result, expected_result)

    def test_calculate_block_volume_success(self):
        """
        Test calculate_block_volume with new sets_data structure
        Should calculate volume from exercises using get_exercises_by_day
        """
        # Mock block data
        mock_block = {
            "block_id": "block123",
            "athlete_id": "athlete123",
            "title": "Test Block",
            "start_date": "2024-01-01",
            "end_date": "2024-01-28",
        }

        # Mock weeks and days
        mock_weeks = [
            {"week_id": "week1", "week_number": 1},
            {"week_id": "week2", "week_number": 2},
        ]

        mock_days_week1 = [{"day_id": "day1", "week_id": "week1"}]
        mock_days_week2 = [{"day_id": "day2", "week_id": "week2"}]

        # Mock exercises with sets_data
        mock_exercises_day1 = [
            {
                "exercise_id": "ex1",
                "exercise_type": "squat",
                "status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 100,
                        "completed": True,
                    },  # 500
                    {
                        "set_number": 2,
                        "reps": 5,
                        "weight": 105,
                        "completed": True,
                    },  # 525
                ],
            }
        ]

        mock_exercises_day2 = [
            {
                "exercise_id": "ex2",
                "exercise_type": "deadlift",
                "status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 3,
                        "weight": 150,
                        "completed": True,
                    },  # 450
                ],
            }
        ]

        # Configure mocks
        self.block_repository_mock.get_block.return_value = mock_block
        self.week_repository_mock.get_weeks_by_block.return_value = mock_weeks
        self.day_repository_mock.get_days_by_week.side_effect = [
            mock_days_week1,
            mock_days_week2,
        ]
        self.exercise_repository_mock.get_exercises_by_day.side_effect = [
            mock_exercises_day1,
            mock_exercises_day2,
        ]

        result = self.analytics_service.calculate_block_volume("block123")

        # Assert repository calls
        self.block_repository_mock.get_block.assert_called_once_with("block123")
        self.week_repository_mock.get_weeks_by_block.assert_called_once_with("block123")
        self.exercise_repository_mock.get_exercises_by_day.assert_any_call("day1")
        self.exercise_repository_mock.get_exercises_by_day.assert_any_call("day2")

        # Assert calculations
        # Week 1: 500 + 525 = 1025
        # Week 2: 450
        # Total: 1475
        expected_result = {
            "block_id": "block123",
            "block_title": "Test Block",
            "total_volume": 1475,
            "weekly_volumes": {
                "week1": {"week_number": 1, "volume": 1025},
                "week2": {"week_number": 2, "volume": 450},
            },
            "exercise_volumes": {"squat": 1025, "deadlift": 450},
            "start_date": "2024-01-01",
            "end_date": "2024-01-28",
        }
        self.assertEqual(result, expected_result)

    def test_calculate_volume_with_repository_exception(self):
        """
        Test calculate_volume when repository raises an exception
        Should return empty list and handle gracefully
        """
        # Configure mock to raise exception
        self.exercise_repository_mock.get_exercises_with_workout_context.side_effect = (
            Exception("Database error")
        )

        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 1, 8)
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.calculate_volume("athlete123", "week")

        # Should return empty list and not crash
        self.assertEqual(result, [])

    def test_calculate_volume_with_invalid_numeric_values(self):
        """
        Test calculate_volume with invalid numeric values in sets_data
        Should skip invalid sets and continue processing
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": "invalid",
                        "weight": 100,
                        "completed": True,
                    },  # Invalid reps
                    {
                        "set_number": 2,
                        "reps": 5,
                        "weight": "bad",
                        "completed": True,
                    },  # Invalid weight
                    {
                        "set_number": 3,
                        "reps": 5,
                        "weight": 100,
                        "completed": True,
                    },  # Valid: 500
                ],
            }
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 1, 8)
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.calculate_volume("athlete123", "week")

        # Should only count the valid set: 5*100 = 500
        expected_result = [{"date": "2024-01-01", "volume": 500}]
        self.assertEqual(result, expected_result)

    def test_compare_blocks_success(self):
        """
        Test successful block comparison using the fixed calculate_block_volume
        Should compare total volumes and exercise-specific volumes
        """
        # Mock block volume calculations
        block1_volume = {
            "block_id": "block1",
            "block_title": "Block 1",
            "total_volume": 10000,
            "exercise_volumes": {"squat": 5000, "bench": 3000, "deadlift": 2000},
        }

        block2_volume = {
            "block_id": "block2",
            "block_title": "Block 2",
            "total_volume": 12000,
            "exercise_volumes": {"squat": 6000, "bench": 3000, "deadlift": 3000},
        }

        # Mock the calculate_block_volume method
        with patch.object(
            self.analytics_service, "calculate_block_volume"
        ) as mock_calc:
            mock_calc.side_effect = [block1_volume, block2_volume]

            result = self.analytics_service.compare_blocks("block1", "block2")

        # Assert comparison calculations
        expected_result = {
            "block1": {"id": "block1", "title": "Block 1", "total_volume": 10000},
            "block2": {"id": "block2", "title": "Block 2", "total_volume": 12000},
            "comparison": {
                "volume_difference": 2000,
                "volume_percent_change": 20.0,
                "exercise_comparison": {
                    "squat": {
                        "block1_volume": 5000,
                        "block2_volume": 6000,
                        "difference": 1000,
                        "percent_change": 20.0,
                    },
                    "bench": {
                        "block1_volume": 3000,
                        "block2_volume": 3000,
                        "difference": 0,
                        "percent_change": 0.0,
                    },
                    "deadlift": {
                        "block1_volume": 2000,
                        "block2_volume": 3000,
                        "difference": 1000,
                        "percent_change": 50.0,
                    },
                },
            },
        }
        self.assertEqual(result, expected_result)

    def test_missing_required_parameters(self):
        """
        Test methods with missing required parameters
        Should return appropriate error responses or empty results
        """
        # Test get_max_weight_history with missing parameters
        result = self.analytics_service.get_max_weight_history("", "squat")
        self.assertEqual(result, [])

        result = self.analytics_service.get_max_weight_history("athlete123", "")
        self.assertEqual(result, [])

        # Test calculate_volume with missing athlete_id
        result = self.analytics_service.calculate_volume("", "week")
        self.assertEqual(result, [])

        # Test get_exercise_frequency with missing parameters
        result = self.analytics_service.get_exercise_frequency("", "squat", "month")
        self.assertIn("error", result)

        result = self.analytics_service.get_exercise_frequency(
            "athlete123", "", "month"
        )
        self.assertIn("error", result)

        # Test calculate_block_volume with missing block_id
        result = self.analytics_service.calculate_block_volume("")
        self.assertEqual(result, {"error": "Block ID is required"})

        # Test compare_blocks with missing parameters
        result = self.analytics_service.compare_blocks("", "block2")
        self.assertEqual(result, {"error": "Both block IDs are required"})

    def test_helper_methods_edge_cases(self):
        """
        Test edge cases for helper methods
        Should handle missing data gracefully
        """
        # Test _calculate_exercise_volume with invalid data types
        exercise_invalid = {
            "sets_data": [
                {"set_number": 1, "reps": None, "weight": 100, "completed": True},
                {"set_number": 2, "reps": 5, "weight": None, "completed": True},
            ]
        }
        volume = self.analytics_service._calculate_exercise_volume(exercise_invalid)
        self.assertEqual(volume, 0.0)

        # Test _is_exercise_analytics_complete with missing sets_data
        exercise_no_sets = {
            "status": "completed",
            "workout_status": "completed",
            "sets_data": [],
        }
        is_complete = self.analytics_service._is_exercise_analytics_complete(
            exercise_no_sets
        )
        self.assertFalse(is_complete)

        # Test _get_max_weight_from_exercise with no completed sets
        exercise_no_completed = {
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 100, "completed": False},
                {"set_number": 2, "reps": 5, "weight": 105, "completed": False},
            ]
        }
        max_weight = self.analytics_service._get_max_weight_from_exercise(
            exercise_no_completed
        )
        self.assertEqual(max_weight, 0.0)

        # Test _get_max_weight_from_exercise with missing weight field (line 83-84)
        exercise_missing_weight = {
            "sets_data": [
                {"set_number": 1, "reps": 5, "completed": True},  # Missing weight
                {"set_number": 2, "reps": 5, "weight": 100, "completed": True},
            ]
        }
        max_weight = self.analytics_service._get_max_weight_from_exercise(
            exercise_missing_weight
        )
        self.assertEqual(max_weight, 100.0)  # Should use the valid weight

        # Test _get_max_weight_from_exercise with invalid weight type (line 83-84)
        exercise_invalid_weight = {
            "sets_data": [
                {
                    "set_number": 1,
                    "reps": 5,
                    "weight": "invalid",
                    "completed": True,
                },  # Invalid weight
                {"set_number": 2, "reps": 5, "weight": 100, "completed": True},
            ]
        }
        max_weight = self.analytics_service._get_max_weight_from_exercise(
            exercise_invalid_weight
        )
        self.assertEqual(max_weight, 100.0)

    def test_get_max_weight_history_missing_date_or_weight(self):
        """
        Test get_max_weight_history with exercises missing date or weight (lines 142-144)
        Should skip exercises with missing required fields
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "exercise_type": "squat",
                "status": "completed",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                ],
            },  # Missing workout_date
            {
                "exercise_id": "ex2",
                "exercise_type": "squat",
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 0,
                        "completed": True,
                    },  # Zero weight
                ],
            },
            {
                "exercise_id": "ex3",
                "exercise_type": "squat",
                "status": "completed",
                "workout_date": "2024-01-02",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 150, "completed": True},
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        result = self.analytics_service.get_max_weight_history("athlete123", "squat")

        # Should only include ex3 (has valid date and weight > 0)
        expected_result = [{"date": "2024-01-02", "max_weight": 150}]
        self.assertEqual(result, expected_result)

    def test_calculate_volume_missing_workout_date(self):
        """
        Test calculate_volume with exercises missing workout_date (lines 167-174)
        Should skip exercises without valid workout_date
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "status": "completed",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                ],
            },  # Missing workout_date
            {
                "exercise_id": "ex2",
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 1, 8)
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.calculate_volume("athlete123", "week")

        # Should only include ex2
        expected_result = [{"date": "2024-01-01", "volume": 500}]
        self.assertEqual(result, expected_result)

    def test_get_exercise_frequency_missing_workout_date(self):
        """
        Test get_exercise_frequency with exercises missing workout_date
        Should skip exercises without valid workout_date for training_days but still count sets
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "exercise_type": "squat",  # Add exercise_type for filtering
                "status": "completed",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                    {"set_number": 2, "reps": 5, "weight": 105, "completed": True},
                ],
            },  # Missing workout_date - sets should still be counted but not training days
            {
                "exercise_id": "ex2",
                "exercise_type": "squat",  # Add exercise_type for filtering
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                ],
            },
            {
                "exercise_id": "ex3",
                "exercise_type": "deadlift",  # Different exercise type - should be filtered out
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 200, "completed": True},
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 1, 31)
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.get_exercise_frequency(
                "athlete123", "squat", "month"
            )

        # Should count all squat sets (2 + 1 = 3) but only 1 training day (ex2 has valid date)
        # ex3 is filtered out because it's a deadlift, not squat
        expected_result = {
            "exercise_type": "squat",
            "time_period": "month",
            "training_days": 1,  # Only ex2 has valid date
            "total_sets": 3,  # All completed sets from squat exercises (2 from ex1 + 1 from ex2)
            "frequency_per_week": 0.23,  # 1 day / (30/7)
            "period_days": 30,
        }
        self.assertEqual(result, expected_result)

    def test_get_exercise_frequency_with_repository_exception(self):
        """
        Test get_exercise_frequency when repository raises exception (lines 242-247)
        Should return error response when repository fails
        """
        self.exercise_repository_mock.get_exercises_with_workout_context.side_effect = (
            Exception("Database error")
        )

        result = self.analytics_service.get_exercise_frequency(
            "athlete123", "squat", "month"
        )

        self.assertIn("error", result)
        self.assertIn("Failed to calculate exercise frequency", result["error"])

    def test_calculate_block_volume_block_not_found(self):
        """
        Test calculate_block_volume when block is not found (lines 292-294)
        Should return error when block doesn't exist
        """
        self.block_repository_mock.get_block.return_value = None

        result = self.analytics_service.calculate_block_volume("nonexistent_block")

        expected_result = {"error": "Block not found"}
        self.assertEqual(result, expected_result)

    def test_calculate_block_volume_missing_week_id_and_day_id(self):
        """
        Test calculate_block_volume with missing week_id and day_id (lines 311, 318)
        Should skip weeks and days with missing IDs
        """
        mock_block = {
            "block_id": "block123",
            "athlete_id": "athlete123",
            "title": "Test Block",
            "start_date": "2024-01-01",
            "end_date": "2024-01-28",
        }

        mock_weeks = [
            {"week_number": 1},  # Missing week_id
            {"week_id": "week2", "week_number": 2},
        ]

        mock_days = [
            {"week_id": "week2"},  # Missing day_id
            {"day_id": "day2", "week_id": "week2"},
        ]

        self.block_repository_mock.get_block.return_value = mock_block
        self.week_repository_mock.get_weeks_by_block.return_value = mock_weeks
        self.day_repository_mock.get_days_by_week.return_value = mock_days
        self.exercise_repository_mock.get_exercises_by_day.return_value = []

        result = self.analytics_service.calculate_block_volume("block123")

        # Should complete successfully, only processing valid week and day
        self.assertEqual(result["block_id"], "block123")
        self.assertEqual(result["total_volume"], 0.0)

        # Should only call get_days_by_week for valid week, and get_exercises_by_day for valid day
        self.day_repository_mock.get_days_by_week.assert_called_once_with("week2")
        self.exercise_repository_mock.get_exercises_by_day.assert_called_once_with(
            "day2"
        )

    def test_compare_blocks_with_calculation_errors(self):
        """
        Test compare_blocks when calculate_block_volume returns errors (lines 397-399)
        Should handle errors from block volume calculations
        """
        # Mock one successful and one error response
        with patch.object(
            self.analytics_service, "calculate_block_volume"
        ) as mock_calc:
            mock_calc.side_effect = [
                {"error": "Block 1 not found"},
                {
                    "block_id": "block2",
                    "block_title": "Block 2",
                    "total_volume": 1000,
                    "exercise_volumes": {},
                },
            ]

            result = self.analytics_service.compare_blocks("block1", "block2")

        expected_result = {
            "error": "One or both blocks could not be analyzed",
            "block1_error": "Block 1 not found",
            "block2_error": None,
        }
        self.assertEqual(result, expected_result)

    def test_compare_blocks_zero_volume_edge_cases(self):
        """
        Test compare_blocks with zero volumes (lines 419, 476-478)
        Should handle division by zero and new exercise cases
        """
        block1_volume = {
            "block_id": "block1",
            "block_title": "Block 1",
            "total_volume": 0,
            "exercise_volumes": {"squat": 0, "bench": 0},
        }

        block2_volume = {
            "block_id": "block2",
            "block_title": "Block 2",
            "total_volume": 1000,
            "exercise_volumes": {"squat": 500, "deadlift": 500},  # New exercise
        }

        with patch.object(
            self.analytics_service, "calculate_block_volume"
        ) as mock_calc:
            mock_calc.side_effect = [block1_volume, block2_volume]

            result = self.analytics_service.compare_blocks("block1", "block2")

        # Should handle zero division gracefully
        comparison = result["comparison"]
        self.assertEqual(comparison["volume_percent_change"], 0)

        # Check exercise comparisons
        squat_comparison = comparison["exercise_comparison"]["squat"]
        self.assertEqual(squat_comparison["percent_change"], 100.0)  # 0 to 500 = 100%

        bench_comparison = comparison["exercise_comparison"]["bench"]
        self.assertEqual(bench_comparison["percent_change"], 0.0)  # 0 to 0 = 0%

        deadlift_comparison = comparison["exercise_comparison"]["deadlift"]
        self.assertEqual(
            deadlift_comparison["percent_change"], 100.0
        )  # New exercise = 100%

    def test_get_exercise_frequency_different_time_periods(self):
        """
        Test get_exercise_frequency with different time periods (lines 194)
        Should handle year, week, and default time periods correctly
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "status": "completed",
                "workout_date": "2024-01-01",
                "workout_status": "completed",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                ],
            }
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        # Test year time period
        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 12, 31)
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.get_exercise_frequency(
                "athlete123", "squat", "year"
            )

        self.assertEqual(result["period_days"], 365)

        # Test week time period
        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 1, 8)
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.get_exercise_frequency(
                "athlete123", "squat", "week"
            )

        self.assertEqual(result["period_days"], 7)

        # Test unknown time period (should default to all time)
        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 1, 8)
            mock_dt.timedelta = dt.timedelta
            mock_dt.datetime.side_effect = lambda *args, **kwargs: dt.datetime(
                *args, **kwargs
            )

            result = self.analytics_service.get_exercise_frequency(
                "athlete123", "squat", "unknown"
            )

        # Should calculate days from 2000-01-01 to now
        expected_days = (dt.datetime(2024, 1, 8) - dt.datetime(2000, 1, 1)).days
        self.assertEqual(result["period_days"], expected_days)

    def test_get_max_weight_from_exercise_with_completed_sets(self):
        """
        Test _get_max_weight_from_exercise helper method with completed sets_data
        Should return the highest weight from completed sets only
        """
        exercise = {
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                {"set_number": 2, "reps": 3, "weight": 120, "completed": True},
                {
                    "set_number": 3,
                    "reps": 1,
                    "weight": 140,
                    "completed": False,
                },  # Not completed
                {"set_number": 4, "reps": 2, "weight": 110, "completed": True},
            ]
        }

        max_weight = self.analytics_service._get_max_weight_from_exercise(exercise)

        # Should return 120 (highest completed weight), not 140 (incomplete)
        expected_max = 120.0
        self.assertEqual(max_weight, expected_max)

    def test_get_max_weight_from_exercise_no_completed_sets(self):
        """
        Test _get_max_weight_from_exercise with no completed sets
        Should return 0.0 when no sets are completed
        """
        exercise = {
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 100, "completed": False},
                {"set_number": 2, "reps": 3, "weight": 120, "completed": False},
            ]
        }

        max_weight = self.analytics_service._get_max_weight_from_exercise(exercise)
        self.assertEqual(max_weight, 0.0)

    def test_get_max_weight_from_exercise_empty_sets_data(self):
        """
        Test _get_max_weight_from_exercise with empty or missing sets_data
        Should return 0.0 when no sets_data available
        """
        exercise_empty = {"sets_data": []}
        exercise_missing = {}

        max_weight_empty = self.analytics_service._get_max_weight_from_exercise(
            exercise_empty
        )
        max_weight_missing = self.analytics_service._get_max_weight_from_exercise(
            exercise_missing
        )

        self.assertEqual(max_weight_empty, 0.0)
        self.assertEqual(max_weight_missing, 0.0)

    def test_get_max_weight_from_exercise_invalid_data_types(self):
        """
        Test _get_max_weight_from_exercise with invalid weight data types
        Should handle ValueError/TypeError gracefully and skip invalid sets
        """
        exercise = {
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": "invalid", "completed": True},
                {"set_number": 2, "reps": 3, "weight": 120, "completed": True},
                {"set_number": 3, "reps": 2, "weight": None, "completed": True},
            ]
        }

        max_weight = self.analytics_service._get_max_weight_from_exercise(exercise)

        # Should return 120, skipping invalid weights
        self.assertEqual(max_weight, 120.0)

    def test_get_all_time_max_weight_single_exercise_type(self):
        """
        Test get_all_time_max_weight with single exercise type across multiple workouts
        Should return the absolute highest weight across all time periods
        """
        # Mock repository to return deadlift exercises from different dates
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "exercise_type": "deadlift",
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-01-01",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                    {"set_number": 2, "reps": 3, "weight": 120, "completed": True},
                ],
            },
            {
                "exercise_id": "ex2",
                "exercise_type": "deadlift",
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-02-01",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 130, "completed": True},
                    {
                        "set_number": 2,
                        "reps": 1,
                        "weight": 150,
                        "completed": True,
                    },  # All-time max
                ],
            },
            {
                "exercise_id": "ex3",
                "exercise_type": "deadlift",
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-03-01",
                "sets_data": [
                    {"set_number": 1, "reps": 3, "weight": 140, "completed": True},
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        max_weight = self.analytics_service.get_all_time_max_weight(
            "test-athlete-id", "deadlift"
        )

        # Should return 150 (absolute highest across all workouts)
        self.assertEqual(max_weight, 150.0)
        self.exercise_repository_mock.get_exercises_with_workout_context.assert_called_once_with(
            athlete_id="test-athlete-id"
        )

    def test_get_all_time_max_weight_case_insensitive_exercise_type(self):
        """
        Test get_all_time_max_weight with case variations in exercise_type
        Should match exercise types case-insensitively
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "exercise_type": "Deadlift",  # Capital D
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-01-01",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                ],
            },
            {
                "exercise_id": "ex2",
                "exercise_type": "DEADLIFT",  # All caps
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-02-01",
                "sets_data": [
                    {"set_number": 1, "reps": 3, "weight": 120, "completed": True},
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        max_weight = self.analytics_service.get_all_time_max_weight(
            "test-athlete-id", "deadlift"
        )

        # Should find both exercises and return max weight 120
        self.assertEqual(max_weight, 120.0)

    def test_get_all_time_max_weight_filters_incomplete_exercises(self):
        """
        Test get_all_time_max_weight includes all exercises with at least one completed set
        Exercise status and workout status are no longer checked
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "exercise_type": "deadlift",
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-01-01",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                ],
            },
            {
                "exercise_id": "ex2",
                "exercise_type": "deadlift",
                "status": "draft",  # Not completed
                "workout_status": "completed",
                "workout_date": "2025-02-01",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 1,
                        "weight": 200,
                        "completed": True,
                    },  # Higher weight but incomplete
                ],
            },
            {
                "exercise_id": "ex3",
                "exercise_type": "deadlift",
                "status": "completed",
                "workout_status": "draft",  # Workout not completed
                "workout_date": "2025-03-01",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 1,
                        "weight": 180,
                        "completed": True,
                    },  # Higher weight but incomplete workout
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        max_weight = self.analytics_service.get_all_time_max_weight(
            "test-athlete-id", "deadlift"
        )

        # All exercises with completed sets are included (ex1, ex2, ex3)
        # exercise status and workout status no longer checked
        # ex2 has weight 200 (highest), so max is 200
        self.assertEqual(max_weight, 200.0)

    def test_get_all_time_max_weight_no_matching_exercises(self):
        """
        Test get_all_time_max_weight with no exercises matching the exercise type
        Should return 0.0 when no exercises of specified type exist
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "exercise_type": "squat",  # Different exercise type
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-01-01",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 100, "completed": True},
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        max_weight = self.analytics_service.get_all_time_max_weight(
            "test-athlete-id", "deadlift"
        )

        # Should return 0.0 when no deadlifts found
        self.assertEqual(max_weight, 0.0)

    def test_get_all_time_max_weight_empty_parameters(self):
        """
        Test get_all_time_max_weight with empty or None parameters
        Should return 0.0 for invalid inputs
        """
        max_weight_no_athlete = self.analytics_service.get_all_time_max_weight(
            "", "deadlift"
        )
        max_weight_no_exercise = self.analytics_service.get_all_time_max_weight(
            "test-athlete-id", ""
        )
        max_weight_none_athlete = self.analytics_service.get_all_time_max_weight(
            None, "deadlift"
        )
        max_weight_none_exercise = self.analytics_service.get_all_time_max_weight(
            "test-athlete-id", None
        )

        self.assertEqual(max_weight_no_athlete, 0.0)
        self.assertEqual(max_weight_no_exercise, 0.0)
        self.assertEqual(max_weight_none_athlete, 0.0)
        self.assertEqual(max_weight_none_exercise, 0.0)

    def test_get_all_time_max_weight_repository_exception(self):
        """
        Test get_all_time_max_weight handles repository exceptions gracefully
        Should return 0.0 and log error when repository throws exception
        """
        # Mock repository to throw exception
        self.exercise_repository_mock.get_exercises_with_workout_context.side_effect = (
            Exception("Database error")
        )

        with patch("builtins.print") as mock_print:
            max_weight = self.analytics_service.get_all_time_max_weight(
                "test-athlete-id", "deadlift"
            )

        # Should return 0.0 and log error
        self.assertEqual(max_weight, 0.0)
        mock_print.assert_called_once()
        self.assertIn("Error in get_all_time_max_weight", mock_print.call_args[0][0])

    def test_get_all_time_max_weight_multiple_exercise_types_filtered(self):
        """
        Test get_all_time_max_weight correctly filters by exercise type among mixed exercises
        Should only consider the specified exercise type, ignoring others
        """
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "exercise_type": "deadlift",
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-01-01",
                "sets_data": [
                    {"set_number": 1, "reps": 5, "weight": 120, "completed": True},
                ],
            },
            {
                "exercise_id": "ex2",
                "exercise_type": "squat",
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-01-01",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 200,
                        "completed": True,
                    },  # Higher weight but different exercise
                ],
            },
            {
                "exercise_id": "ex3",
                "exercise_type": "bench press",
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-01-01",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 150,
                        "completed": True,
                    },  # Higher weight but different exercise
                ],
            },
            {
                "exercise_id": "ex4",
                "exercise_type": "deadlift",
                "status": "completed",
                "workout_status": "completed",
                "workout_date": "2025-02-01",
                "sets_data": [
                    {
                        "set_number": 1,
                        "reps": 3,
                        "weight": 140,
                        "completed": True,
                    },  # Highest deadlift
                ],
            },
        ]

        self.exercise_repository_mock.get_exercises_with_workout_context.return_value = (
            mock_exercises
        )

        max_weight = self.analytics_service.get_all_time_max_weight(
            "test-athlete-id", "deadlift"
        )

        # Should return 140 (highest deadlift), ignoring 200 (squat) and 150 (bench press)
        self.assertEqual(max_weight, 140.0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
