import unittest
from unittest.mock import MagicMock, patch
from src.services.analytics_service import AnalyticsService
import datetime as dt


class TestAnalyticsService(unittest.TestCase):
    """
    Test suite for the AnalyticsService class
    """

    def setUp(self):
        """
        Set up test environment before each test method
        """
        # Mock all repository dependencies
        self.workout_repository_mock = MagicMock()
        self.exercise_repository_mock = MagicMock()
        self.block_repository_mock = MagicMock()
        self.week_repository_mock = MagicMock()
        self.day_repository_mock = MagicMock()

        # Initialize service with mocked repositories
        with patch(
            "src.services.analytics_service.WorkoutRepository",
            return_value=self.workout_repository_mock,
        ), patch(
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

    def test_get_max_weight_history_success(self):
        """
        Test retrieving max weight history for an exercise type
        """
        # Mock data - exercises on different dates with varying weights
        # Using current data model structure
        mock_exercises = [
            {
                "date": "2024-01-01",
                "weight": 100,
                "exercise_type": "squat",
                "status": "completed",
                "workout_status": "completed",
            },
            {
                "date": "2024-01-01",
                "weight": 105,
                "exercise_type": "squat",
                "status": "completed",
                "workout_status": "completed",
            },  # Higher weight same day
            {
                "date": "2024-01-08",
                "weight": 110,
                "exercise_type": "squat",
                "status": "completed",
                "workout_status": "completed",
            },
            {
                "date": "2024-01-15",
                "weight": 108,
                "exercise_type": "squat",
                "status": "completed",
                "workout_status": "completed",
            },  # Lower than previous
        ]

        # Configure mock to return test data
        self.workout_repository_mock.get_exercises_by_type.return_value = mock_exercises

        # Call the service method
        result = self.analytics_service.get_max_weight_history("athlete123", "squat")

        # Assert repository was called with correct parameters
        self.workout_repository_mock.get_exercises_by_type.assert_called_once_with(
            "athlete123", "squat"
        )

        # Assert the result is correctly processed
        expected_result = [
            {"date": "2024-01-01", "max_weight": 105},  # Max for this date
            {"date": "2024-01-08", "max_weight": 110},
            {"date": "2024-01-15", "max_weight": 108},
        ]
        self.assertEqual(result, expected_result)

    def test_get_max_weight_history_filters_incomplete_exercises(self):
        """
        Test that max weight history only includes completed exercises
        """
        # Mock data with mix of completed and incomplete exercises
        mock_exercises = [
            {
                "date": "2024-01-01",
                "weight": 100,
                "exercise_type": "squat",
                "status": "completed",
                "workout_status": "completed",
            },
            {
                "date": "2024-01-01",
                "weight": 200,
                "exercise_type": "squat",
                "status": "planned",  # Not completed
                "workout_status": "completed",
            },
            {
                "date": "2024-01-02",
                "weight": 105,
                "exercise_type": "squat",
                "status": "completed",
                "workout_status": "in_progress",  # Workout not completed
            },
        ]

        self.workout_repository_mock.get_exercises_by_type.return_value = mock_exercises

        result = self.analytics_service.get_max_weight_history("athlete123", "squat")

        # Should only include the first exercise (completed exercise in completed workout)
        expected_result = [{"date": "2024-01-01", "max_weight": 100}]
        self.assertEqual(result, expected_result)

    def test_calculate_volume_weekly(self):
        """
        Test volume calculation for weekly time period using current data structure
        """
        # Mock workout data using current Workout model structure
        mock_workouts = [
            {
                "date": "2024-01-01",
                "status": "completed",
                "exercises": [
                    {"sets": 3, "reps": 5, "weight": 100, "status": "completed"},
                    {"sets": 3, "reps": 8, "weight": 80, "status": "completed"},
                ],
            },
            {
                "date": "2024-01-03",
                "status": "completed",
                "exercises": [
                    {"sets": 4, "reps": 6, "weight": 120, "status": "completed"},
                ],
            },
        ]

        # Configure mock
        self.workout_repository_mock.get_completed_workouts_since.return_value = (
            mock_workouts
        )

        # Call the service method with proper datetime mocking
        with patch("src.services.analytics_service.dt") as mock_dt:
            # Create real datetime objects for calculations
            mock_now = dt.datetime(2024, 1, 8)
            mock_dt.datetime.now.return_value = mock_now
            mock_dt.timedelta = dt.timedelta  # Use real timedelta

            # Call the service method
            result = self.analytics_service.calculate_volume("athlete123", "week")

        # Assert repository was called with correct start date
        # 2024-01-08 - 7 days = 2024-01-01
        expected_start_date = "2024-01-01"
        self.workout_repository_mock.get_completed_workouts_since.assert_called_once_with(
            "athlete123", expected_start_date
        )

        # Assert volume calculations
        # Day 1: (3*5*100) + (3*8*80) = 1500 + 1920 = 3420
        # Day 3: (4*6*120) = 2880
        expected_result = [
            {"date": "2024-01-01", "volume": 3420},
            {"date": "2024-01-03", "volume": 2880},
        ]
        self.assertEqual(result, expected_result)

    def test_calculate_volume_only_counts_completed_exercises(self):
        """
        Test that volume calculation only includes completed exercises
        """
        # Mock workout with mix of completed and incomplete exercises
        mock_workouts = [
            {
                "date": "2024-01-01",
                "status": "completed",
                "exercises": [
                    {
                        "sets": 3,
                        "reps": 5,
                        "weight": 100,
                        "status": "completed",
                    },  # Valid
                    {
                        "sets": 3,
                        "reps": 5,
                        "weight": 100,
                        "status": "planned",
                    },  # Not completed
                    {
                        "sets": 3,
                        "reps": 5,
                        "weight": 100,
                        "status": "skipped",
                    },  # Skipped
                ],
            }
        ]

        self.workout_repository_mock.get_completed_workouts_since.return_value = (
            mock_workouts
        )

        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = dt.datetime(2024, 1, 8)
            result = self.analytics_service.calculate_volume("athlete123", "week")

        # Should only count the completed exercise: 3*5*100 = 1500
        expected_result = [{"date": "2024-01-01", "volume": 1500}]
        self.assertEqual(result, expected_result)

    def test_calculate_block_volume_success(self):
        """
        Test successful block volume calculation with current data structure
        """
        # Mock block data
        mock_block = {
            "block_id": "block123",
            "athlete_id": "athlete123",
            "title": "Test Block",
            "start_date": "2024-01-01",
            "end_date": "2024-01-28",
        }

        # Mock weeks data
        mock_weeks = [
            {"week_id": "week1", "week_number": 1},
            {"week_id": "week2", "week_number": 2},
        ]

        # Mock days data
        mock_days_week1 = [
            {"day_id": "day1", "week_id": "week1"},
            {"day_id": "day2", "week_id": "week1"},
        ]
        mock_days_week2 = [{"day_id": "day3", "week_id": "week2"}]

        # Mock workout data using current structure
        mock_workout1 = {
            "day_id": "day1",
            "status": "completed",
            "exercises": [
                {
                    "sets": 3,
                    "reps": 5,
                    "weight": 100,
                    "exercise_type": "squat",
                    "status": "completed",
                }
            ],
        }
        mock_workout2 = {
            "day_id": "day3",
            "status": "completed",
            "exercises": [
                {
                    "sets": 4,
                    "reps": 6,
                    "weight": 120,
                    "exercise_type": "deadlift",
                    "status": "completed",
                }
            ],
        }

        # Configure mocks
        self.block_repository_mock.get_block.return_value = mock_block
        self.week_repository_mock.get_weeks_by_block.return_value = mock_weeks
        self.day_repository_mock.get_days_by_week.side_effect = [
            mock_days_week1,
            mock_days_week2,
        ]
        self.workout_repository_mock.get_workout_by_day.side_effect = [
            mock_workout1,  # day1
            None,  # day2 - no workout
            mock_workout2,  # day3
        ]

        # Call the service method
        result = self.analytics_service.calculate_block_volume("block123")

        # Assert repository calls
        self.block_repository_mock.get_block.assert_called_once_with("block123")
        self.week_repository_mock.get_weeks_by_block.assert_called_once_with("block123")

        # Assert calculations
        # Workout 1: 3*5*100 = 1500
        # Workout 2: 4*6*120 = 2880
        # Total: 4380
        expected_result = {
            "block_id": "block123",
            "block_title": "Test Block",
            "total_volume": 4380,
            "weekly_volumes": {
                "week1": {"week_number": 1, "volume": 1500},
                "week2": {"week_number": 2, "volume": 2880},
            },
            "exercise_volumes": {"squat": 1500, "deadlift": 2880},
            "start_date": "2024-01-01",
            "end_date": "2024-01-28",
        }
        self.assertEqual(result, expected_result)

    def test_calculate_volume_with_repository_exception(self):
        """
        Test volume calculation when repository raises an exception (line 134-136)
        """
        # Configure mock to raise exception
        self.workout_repository_mock.get_completed_workouts_since.side_effect = (
            Exception("Database error")
        )

        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 1, 8)
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.calculate_volume("athlete123", "week")

        # Should return empty list and not crash
        self.assertEqual(result, [])

    def test_calculate_volume_with_workout_missing_date(self):
        """
        Test volume calculation with workouts missing date field (line 140)
        """
        mock_workouts = [
            {
                # Missing date field
                "status": "completed",
                "exercises": [
                    {"sets": 3, "reps": 5, "weight": 100, "status": "completed"}
                ],
            },
            {
                "date": "2024-01-02",
                "status": "completed",
                "exercises": [
                    {"sets": 4, "reps": 6, "weight": 120, "status": "completed"}
                ],
            },
        ]

        self.workout_repository_mock.get_completed_workouts_since.return_value = (
            mock_workouts
        )

        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 1, 8)
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.calculate_volume("athlete123", "week")

        # Should only include workout with valid date
        expected_result = [{"date": "2024-01-02", "volume": 2880}]  # 4*6*120
        self.assertEqual(result, expected_result)

    def test_calculate_volume_with_invalid_numeric_values(self):
        """
        Test volume calculation with invalid numeric values (line 166)
        """
        mock_workouts = [
            {
                "date": "2024-01-01",
                "status": "completed",
                "exercises": [
                    {
                        "sets": "invalid",
                        "reps": 5,
                        "weight": 100,
                        "status": "completed",
                    },  # Invalid sets
                    {
                        "sets": 3,
                        "reps": "bad",
                        "weight": 100,
                        "status": "completed",
                    },  # Invalid reps
                    {
                        "sets": 3,
                        "reps": 5,
                        "weight": "terrible",
                        "status": "completed",
                    },  # Invalid weight
                    {
                        "sets": 3,
                        "reps": 5,
                        "weight": 100,
                        "status": "completed",
                    },  # Valid
                ],
            }
        ]

        self.workout_repository_mock.get_completed_workouts_since.return_value = (
            mock_workouts
        )

        with patch("src.services.analytics_service.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2024, 1, 8)
            mock_dt.timedelta = dt.timedelta

            result = self.analytics_service.calculate_volume("athlete123", "week")

        # Should only count the valid exercise: 3*5*100 = 1500
        expected_result = [{"date": "2024-01-01", "volume": 1500}]
        self.assertEqual(result, expected_result)

    def test_calculate_block_volume_with_repository_exception(self):
        """
        Test block volume calculation when repository raises an exception (lines 252-254)
        """
        # Configure mock to raise exception
        self.block_repository_mock.get_block.side_effect = Exception(
            "Database connection failed"
        )

        result = self.analytics_service.calculate_block_volume("block123")

        # Should return error response
        self.assertIn("error", result)
        self.assertIn("Failed to calculate block volume", result["error"])

    def test_calculate_block_volume_with_missing_athlete_id(self):
        """
        Test block volume calculation with block missing athlete_id (line 173)
        """
        # Mock block data without athlete_id
        mock_block = {
            "block_id": "block123",
            "title": "Test Block",
            "start_date": "2024-01-01",
            "end_date": "2024-01-28"
            # Missing athlete_id
        }

        self.block_repository_mock.get_block.return_value = mock_block

        result = self.analytics_service.calculate_block_volume("block123")

        # Should return error response
        expected_result = {"error": "Block missing athlete_id"}
        self.assertEqual(result, expected_result)

    def test_calculate_block_volume_with_missing_week_id(self):
        """
        Test block volume calculation with weeks missing week_id (line 180)
        """
        # Mock block data
        mock_block = {
            "block_id": "block123",
            "athlete_id": "athlete123",
            "title": "Test Block",
            "start_date": "2024-01-01",
            "end_date": "2024-01-28",
        }

        # Mock weeks with missing week_id
        mock_weeks = [
            {"week_number": 1},  # Missing week_id
            {"week_id": "week2", "week_number": 2},  # Valid
        ]

        self.block_repository_mock.get_block.return_value = mock_block
        self.week_repository_mock.get_weeks_by_block.return_value = mock_weeks
        self.day_repository_mock.get_days_by_week.return_value = []

        result = self.analytics_service.calculate_block_volume("block123")

        # Should complete successfully, only processing valid week
        self.assertEqual(result["block_id"], "block123")
        self.assertEqual(result["total_volume"], 0.0)

        # Should only call get_days_by_week for the valid week
        self.day_repository_mock.get_days_by_week.assert_called_once_with("week2")

    def test_calculate_block_volume_with_missing_day_id(self):
        """
        Test block volume calculation with days missing day_id (line 291)
        """
        # Mock block data
        mock_block = {
            "block_id": "block123",
            "athlete_id": "athlete123",
            "title": "Test Block",
            "start_date": "2024-01-01",
            "end_date": "2024-01-28",
        }

        mock_weeks = [{"week_id": "week1", "week_number": 1}]

        # Mock days with missing day_id
        mock_days = [
            {"week_id": "week1"},  # Missing day_id
            {"day_id": "day2", "week_id": "week1"},  # Valid
        ]

        self.block_repository_mock.get_block.return_value = mock_block
        self.week_repository_mock.get_weeks_by_block.return_value = mock_weeks
        self.day_repository_mock.get_days_by_week.return_value = mock_days
        self.workout_repository_mock.get_workout_by_day.return_value = None

        result = self.analytics_service.calculate_block_volume("block123")

        # Should complete successfully, only processing valid day
        self.assertEqual(result["block_id"], "block123")

        # Should only call get_workout_by_day for the valid day
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with(
            "athlete123", "day2"
        )

    def test_calculate_block_volume_with_invalid_exercise_numeric_values(self):
        """
        Test block volume calculation with invalid exercise numeric values (line 300)
        """
        # Mock complete setup with invalid exercise data
        mock_block = {
            "block_id": "block123",
            "athlete_id": "athlete123",
            "title": "Test Block",
            "start_date": "2024-01-01",
            "end_date": "2024-01-28",
        }

        mock_weeks = [{"week_id": "week1", "week_number": 1}]
        mock_days = [{"day_id": "day1", "week_id": "week1"}]

        mock_workout = {
            "day_id": "day1",
            "status": "completed",
            "exercises": [
                {
                    "sets": "invalid",
                    "reps": 5,
                    "weight": 100,
                    "exercise_type": "squat",
                    "status": "completed",
                },
                {
                    "sets": 3,
                    "reps": 5,
                    "weight": 100,
                    "exercise_type": "bench",
                    "status": "completed",
                },  # Valid
            ],
        }

        self.block_repository_mock.get_block.return_value = mock_block
        self.week_repository_mock.get_weeks_by_block.return_value = mock_weeks
        self.day_repository_mock.get_days_by_week.return_value = mock_days
        self.workout_repository_mock.get_workout_by_day.return_value = mock_workout

        result = self.analytics_service.calculate_block_volume("block123")

        # Should only count the valid exercise: 3*5*100 = 1500
        self.assertEqual(result["total_volume"], 1500)
        self.assertEqual(result["exercise_volumes"], {"bench": 1500})

    def test_get_exercise_frequency_success(self):
        """
        Test successful exercise frequency calculation with current data structure
        """
        # Mock exercises over a month period using current structure
        mock_exercises = [
            {
                "date": "2024-01-01",
                "sets": 3,
                "status": "completed",
                "workout_status": "completed",
            },  # Week 1
            {
                "date": "2024-01-03",
                "sets": 4,
                "status": "completed",
                "workout_status": "completed",
            },  # Week 1
            {
                "date": "2024-01-08",
                "sets": 3,
                "status": "completed",
                "workout_status": "completed",
            },  # Week 2
            {
                "date": "2024-01-15",
                "sets": 5,
                "status": "completed",
                "workout_status": "completed",
            },  # Week 3
            {
                "date": "2024-01-15",
                "sets": 3,
                "status": "completed",
                "workout_status": "completed",
            },  # Week 3 (same day)
            {
                "date": "2024-01-22",
                "sets": 4,
                "status": "completed",
                "workout_status": "completed",
            },  # Week 4
        ]

        # Configure mock
        self.workout_repository_mock.get_exercises_by_type.return_value = mock_exercises

        # Call the service method with proper datetime mocking
        with patch("src.services.analytics_service.dt") as mock_dt:
            # Create real datetime objects for calculations
            mock_now = dt.datetime(2024, 1, 31)
            mock_dt.datetime.now.return_value = mock_now
            mock_dt.timedelta = dt.timedelta  # Use real timedelta
            mock_dt.datetime.side_effect = lambda *args, **kwargs: dt.datetime(
                *args, **kwargs
            )  # Real datetime constructor

            # Call the service method
            result = self.analytics_service.get_exercise_frequency(
                "athlete123", "squat", "month"
            )

        # Assert repository was called
        self.workout_repository_mock.get_exercises_by_type.assert_called_once_with(
            "athlete123", "squat"
        )

        # Assert calculations
        # 5 unique training days: 01/01, 01/03, 01/08, 01/15, 01/22
        # Total sets: 3+4+3+5+3+4 = 22
        # Frequency per week: 5 days / (30 days / 7) = 5 / 4.29 ≈ 1.17
        expected_result = {
            "exercise_type": "squat",
            "time_period": "month",
            "training_days": 5,
            "total_sets": 22,
            "frequency_per_week": 1.17,  # Will be rounded to 2 decimal places
            "period_days": 30,
        }
        self.assertEqual(result, expected_result)

    def test_get_max_weight_history_with_repository_exception(self):
        """
        Test max weight history when repository raises an exception (line 87)
        """
        # Configure mock to raise exception
        self.workout_repository_mock.get_exercises_by_type.side_effect = Exception(
            "Database connection failed"
        )

        # Call the service method
        result = self.analytics_service.get_max_weight_history("athlete123", "squat")

        # Should return empty list and not crash
        self.assertEqual(result, [])

    def test_get_max_weight_history_with_missing_weight(self):
        """
        Test max weight history with exercises missing weight data (lines 96-103)
        """
        # Mock exercises with missing or None weight values
        mock_exercises = [
            {
                "date": "2024-01-01",
                "weight": None,
                "status": "completed",
                "workout_status": "completed",
            },
            {
                "date": "2024-01-02",
                "status": "completed",
                "workout_status": "completed",
            },  # Missing weight field
            {
                "date": "2024-01-03",
                "weight": 150,
                "status": "completed",
                "workout_status": "completed",
            },  # Valid
        ]

        self.workout_repository_mock.get_exercises_by_type.return_value = mock_exercises

        result = self.analytics_service.get_max_weight_history("athlete123", "squat")

        # Should only include the valid exercise
        expected_result = [{"date": "2024-01-03", "max_weight": 150}]
        self.assertEqual(result, expected_result)

    def test_compare_blocks_success(self):
        """
        Test successful block comparison
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

            # Call the service method
            result = self.analytics_service.compare_blocks("block1", "block2")

            # Assert both blocks were analyzed
            mock_calc.assert_any_call("block1")
            mock_calc.assert_any_call("block2")

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

    def test_compare_blocks_with_repository_exception(self):
        """
        Test block comparison when calculate_block_volume raises an exception (lines 357-359)
        """
        # Mock calculate_block_volume to raise exception
        with patch.object(
            self.analytics_service, "calculate_block_volume"
        ) as mock_calc:
            mock_calc.side_effect = Exception("Calculation failed")

            result = self.analytics_service.compare_blocks("block1", "block2")

        # Should return error response
        self.assertIn("error", result)
        self.assertIn("Failed to compare blocks", result["error"])

    def test_compare_blocks_with_zero_volume_percent_calculation(self):
        """
        Test block comparison percent calculation edge cases (lines 373, 380-381)
        """
        # Test zero volume in first block (division by zero case)
        block1_volume = {
            "block_id": "block1",
            "block_title": "Block 1",
            "total_volume": 0,  # Zero volume
            "exercise_volumes": {"squat": 0},
        }

        block2_volume = {
            "block_id": "block2",
            "block_title": "Block 2",
            "total_volume": 1000,
            "exercise_volumes": {"squat": 1000},
        }

        with patch.object(
            self.analytics_service, "calculate_block_volume"
        ) as mock_calc:
            mock_calc.side_effect = [block1_volume, block2_volume]

            result = self.analytics_service.compare_blocks("block1", "block2")

        # Should handle division by zero gracefully
        self.assertEqual(result["comparison"]["volume_percent_change"], 0)
        self.assertEqual(
            result["comparison"]["exercise_comparison"]["squat"]["percent_change"],
            100.0,
        )

    def test_error_handling_in_methods(self):
        """
        Test error handling when repository methods raise exceptions
        """
        # Test max weight history with repository exception
        self.workout_repository_mock.get_exercises_by_type.side_effect = Exception(
            "Database error"
        )

        result = self.analytics_service.get_max_weight_history("athlete123", "squat")
        self.assertEqual(result, [])

        # Test volume calculation with repository exception
        self.workout_repository_mock.get_completed_workouts_since.side_effect = (
            Exception("Database error")
        )

        result = self.analytics_service.calculate_volume("athlete123", "week")
        self.assertEqual(result, [])

        # Test block volume with repository exception
        self.block_repository_mock.get_block.side_effect = Exception("Database error")

        result = self.analytics_service.calculate_block_volume("block123")
        self.assertIn("error", result)
        self.assertIn("Failed to calculate block volume", result["error"])

    def test_volume_calculation_edge_cases(self):
        """
        Test volume calculation with edge cases using current data structure
        """
        # Mock workout with mixed valid/invalid data
        mock_workouts = [
            {
                "date": "2024-01-01",
                "status": "completed",
                "exercises": [
                    {
                        "sets": 0,
                        "reps": 5,
                        "weight": 100,
                        "status": "completed",
                    },  # Zero sets
                    {
                        "sets": 3,
                        "reps": 0,
                        "weight": 100,
                        "status": "completed",
                    },  # Zero reps
                    {
                        "sets": 3,
                        "reps": 5,
                        "weight": 0,
                        "status": "completed",
                    },  # Zero weight
                    {
                        "sets": 3,
                        "reps": 5,
                        "weight": 100,
                        "status": "completed",
                    },  # Valid
                ],
            },
            {
                # Workout without date
                "status": "completed",
                "exercises": [
                    {"sets": 3, "reps": 5, "weight": 100, "status": "completed"},
                ],
            },
            {
                "date": "2024-01-02",
                "status": "completed",
                "exercises": [],  # No exercises
            },
        ]

        self.workout_repository_mock.get_completed_workouts_since.return_value = (
            mock_workouts
        )

        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = dt.datetime(2024, 1, 8)
            result = self.analytics_service.calculate_volume("athlete123", "week")

        # Should count all exercises including zero values
        # Day 1: (0*5*100) + (3*0*100) + (3*5*0) + (3*5*100) = 0 + 0 + 0 + 1500 = 1500
        # Day without date: skipped
        # Day 2: No exercises = 0 volume
        expected_result = [
            {"date": "2024-01-01", "volume": 1500},
            {"date": "2024-01-02", "volume": 0},
        ]
        self.assertEqual(result, expected_result)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
