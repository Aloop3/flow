from typing import List, Dict, Any, Union
from src.repositories.exercise_repository import ExerciseRepository
from src.repositories.block_repository import BlockRepository
from src.repositories.week_repository import WeekRepository
from src.repositories.day_repository import DayRepository
import datetime as dt


class AnalyticsService:
    def __init__(self):
        self.exercise_repository: ExerciseRepository = ExerciseRepository()
        self.block_repository: BlockRepository = BlockRepository()
        self.week_repository: WeekRepository = WeekRepository()
        self.day_repository: DayRepository = DayRepository()

    def _calculate_exercise_volume(self, exercise: Dict[str, Any]) -> float:
        """
        Calculate total volume for an exercise from sets_data.
        Volume = sum of (reps × weight) for each completed set.

        :param exercise: Exercise dict with sets_data
        :return: Total volume for the exercise
        """
        sets_data = exercise.get("sets_data", [])
        if not sets_data:
            return 0.0

        total_volume = 0.0
        for set_data in sets_data:
            if set_data.get("completed", False):
                reps = set_data.get("reps", 0)
                weight = set_data.get("weight", 0)
                try:
                    volume = float(reps) * float(weight)
                    total_volume += volume
                except (ValueError, TypeError):
                    continue

        return total_volume

    def _is_exercise_analytics_complete(self, exercise: Dict[str, Any]) -> bool:
        """
        Check if exercise qualifies for analytics.
        Requires at least one completed set in sets_data.
        Does NOT require workout_status='completed' since athletes often
        complete individual exercises without explicitly finishing the workout.

        :param exercise: Exercise dict with sets_data and status
        :return: True if exercise should count in analytics
        """
        # Check at least one set is completed in sets_data
        sets_data = exercise.get("sets_data", [])
        if not sets_data:
            return False

        return any(set_data.get("completed", False) for set_data in sets_data)

    def _get_max_weight_from_exercise(self, exercise: Dict[str, Any]) -> float:
        """
        Get the maximum weight lifted in an exercise from sets_data.

        :param exercise: Exercise dict with sets_data
        :return: Maximum weight from completed sets
        """
        sets_data = exercise.get("sets_data", [])
        if not sets_data:
            return 0.0

        max_weight = 0.0
        for set_data in sets_data:
            if set_data.get("completed", False):
                weight = set_data.get("weight", 0)
                try:
                    weight_float = float(weight)
                    if weight_float > max_weight:
                        max_weight = weight_float
                except (ValueError, TypeError):
                    continue

        return max_weight

    def get_all_time_max_weight(self, athlete_id: str, exercise_type: str) -> float:
        """
        Get the absolute highest weight ever lifted for a specific exercise.
        Used for 1RM display - returns single value, not time series.

        :param athlete_id: The ID of the athlete
        :param exercise_type: Type of exercise ('deadlift', 'squat', 'bench press')
        :return: Highest weight ever lifted for this exercise
        """
        if not athlete_id or not exercise_type:
            return 0.0

        try:
            # Get ALL exercises for athlete (no date filtering)
            exercises = self.exercise_repository.get_exercises_with_workout_context(
                athlete_id=athlete_id
            )

            # Filter by exercise_type (case-insensitive)
            exercises_of_type = [
                exercise
                for exercise in exercises
                if exercise.get("exercise_type", "").lower() == exercise_type.lower()
            ]

            # Filter for analytics-complete exercises only
            completed_exercises = [
                exercise
                for exercise in exercises_of_type
                if self._is_exercise_analytics_complete(exercise)
            ]

            # Find absolute maximum weight across ALL time
            all_time_max = 0.0

            for exercise in completed_exercises:
                exercise_max = self._get_max_weight_from_exercise(exercise)
                if exercise_max > all_time_max:
                    all_time_max = exercise_max

            return all_time_max

        except Exception as e:
            print(f"Error in get_all_time_max_weight: {e}")
            return 0.0

    def get_max_weight_history(
        self, athlete_id: str, exercise_type: str
    ) -> List[Dict[str, Any]]:
        if not athlete_id or not exercise_type:
            return []

        try:
            # Use same pattern as calculate_volume
            exercises = self.exercise_repository.get_exercises_with_workout_context(
                athlete_id=athlete_id  # Remove exercise_type parameter
            )

            # Filter by exercise_type AFTER getting all exercises (case-insensitive)
            exercises_of_type = [
                exercise
                for exercise in exercises
                if exercise.get("exercise_type", "").lower() == exercise_type.lower()
            ]

            # Filter for analytics-complete exercises only
            completed_exercises = [
                exercise
                for exercise in exercises_of_type
                if self._is_exercise_analytics_complete(exercise)
            ]

            # Group exercises by date and find the maximum weight for each day
            max_weight_by_date = {}

            for exercise in completed_exercises:
                date = exercise.get("workout_date")
                if not date:
                    continue

                max_weight = self._get_max_weight_from_exercise(exercise)
                if max_weight > 0:
                    # Update the max weight for this date if it is higher
                    if (
                        date not in max_weight_by_date
                        or max_weight > max_weight_by_date[date]
                    ):
                        max_weight_by_date[date] = max_weight

            # Convert dictionary to list of data points
            max_weight_data = [
                {"date": date, "max_weight": weight}
                for date, weight in max_weight_by_date.items()
            ]

            # Sort the data points chronologically
            max_weight_data.sort(key=lambda x: x["date"])

            return max_weight_data

        except Exception as e:
            print(f"Error in get_max_weight_history: {e}")
            return []

    def calculate_volume(
        self, athlete_id: str, time_period: str
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Calculate training volume over time
        Volume = sum of (reps × weight) for each completed set

        :param athlete_id: The ID of the athlete
        :param time_period: The time period for which to calculate volume (e.g., 'week', 'month', 'year')
        :return: A list of date and volume values
        """
        if not athlete_id:
            return []

        try:
            # Get start date based on time period
            now = dt.datetime.now()

            if time_period == "week":
                start_datetime = now - dt.timedelta(days=7)
                start_date = start_datetime.strftime("%Y-%m-%d")
            elif time_period == "month":
                start_datetime = now - dt.timedelta(days=30)
                start_date = start_datetime.strftime("%Y-%m-%d")
            elif time_period == "year":
                start_datetime = now - dt.timedelta(days=365)
                start_date = start_datetime.strftime("%Y-%m-%d")
            else:
                start_date = "2000-01-01"  # All time

            # Get all exercises for the athlete since start_date
            exercises = self.exercise_repository.get_exercises_with_workout_context(
                athlete_id=athlete_id, start_date=start_date
            )

            # Filter for analytics-complete exercises only
            completed_exercises = [
                exercise
                for exercise in exercises
                if self._is_exercise_analytics_complete(exercise)
            ]

            # Calculate volume for each day
            volume_data = {}

            for exercise in completed_exercises:
                date = exercise.get("workout_date")
                if not date:
                    continue

                exercise_volume = self._calculate_exercise_volume(exercise)

                # Store the total daily volume
                if date in volume_data:
                    volume_data[date] += exercise_volume
                else:
                    volume_data[date] = exercise_volume

            # Convert to list of dicts for easier consumption by frontend
            result = [
                {"date": date, "volume": volume} for date, volume in volume_data.items()
            ]

            # Sort chronologically
            result.sort(key=lambda x: x["date"])

            return result

        except Exception as e:
            print(f"Error in calculate_volume: {e}")
            return []

    def get_exercise_frequency(
        self, athlete_id: str, exercise_type: str, time_period: str = "month"
    ) -> Dict[str, Any]:
        """
        Calculate how often a specific exercise is performed over time
        """
        if not athlete_id or not exercise_type:
            return {"error": "Athlete ID and exercise type are required"}

        try:
            # Get start date based on time period
            now = dt.datetime.now()

            if time_period == "week":
                start_date = (now - dt.timedelta(days=7)).isoformat()[:10]
                period_days = 7
            elif time_period == "month":
                start_date = (now - dt.timedelta(days=30)).isoformat()[:10]
                period_days = 30
            elif time_period == "year":
                start_date = (now - dt.timedelta(days=365)).isoformat()[:10]
                period_days = 365
            else:
                start_date = "2000-01-01"
                period_days = (now - dt.datetime(2000, 1, 1)).days

            # Use same pattern as calculate_volume
            exercises = self.exercise_repository.get_exercises_with_workout_context(
                athlete_id=athlete_id,
                start_date=start_date,  # Remove exercise_type parameter
            )

            # Filter by exercise_type after getting all exercises (case-insensitive)
            exercises_of_type = [
                exercise
                for exercise in exercises
                if exercise.get("exercise_type", "").lower() == exercise_type.lower()
            ]

            # Filter for analytics-complete exercises only
            completed_exercises = [
                exercise
                for exercise in exercises_of_type
                if self._is_exercise_analytics_complete(exercise)
            ]

            # Count unique training days and total sets
            training_dates = set()
            total_sets = 0

            for exercise in completed_exercises:
                date = exercise.get("workout_date")
                if date:
                    training_dates.add(date)

                # Count completed sets from sets_data
                sets_data = exercise.get("sets_data", [])
                completed_sets = sum(
                    1 for set_data in sets_data if set_data.get("completed", False)
                )
                total_sets += completed_sets

            frequency_per_week = (
                len(training_dates) / (period_days / 7) if period_days > 0 else 0
            )

            return {
                "exercise_type": exercise_type,
                "time_period": time_period,
                "training_days": len(training_dates),
                "total_sets": total_sets,
                "frequency_per_week": round(frequency_per_week, 2),
                "period_days": period_days,
            }

        except Exception as e:
            print(f"Error in get_exercise_frequency: {e}")
            return {"error": f"Failed to calculate exercise frequency: {str(e)}"}

    def calculate_block_volume(self, block_id: str) -> Dict[str, Any]:
        """
        Calculate total and weekly training volume for a specific training block

        :param block_id: The ID of the training block
        :return: A dictionary containing the total volume, weekly volumes, and exercise breakdowns
        """
        if not block_id:
            return {"error": "Block ID is required"}

        try:
            # Get the block data to determine athlete and time period
            block_data = self.block_repository.get_block(block_id)

            if not block_data:
                return {"error": "Block not found"}

            athlete_id = block_data.get("athlete_id")
            start_date = block_data.get("start_date")
            end_date = block_data.get("end_date")

            if not athlete_id:
                return {"error": "Block missing athlete_id"}

            # Get all weeks in the block
            weeks = self.week_repository.get_weeks_by_block(block_id)

            # Get all days associated with the block
            all_days = []
            for week in weeks:
                week_id = week.get("week_id")
                if week_id:
                    days = self.day_repository.get_days_by_week(week_id)
                    all_days.extend(days)

            # Get all exercises for these days
            all_exercises = []
            for day in all_days:
                day_id = day.get("day_id")
                if day_id:
                    exercises = self.exercise_repository.get_exercises_by_day(day_id)
                    for exercise in exercises:
                        # Add day and week info to exercise for later reference
                        exercise["_day_data"] = day
                        all_exercises.append(exercise)

            # Calculate total block volume
            total_volume = 0.0
            exercise_volumes = {}
            weekly_volumes = {}

            for exercise in all_exercises:
                # Find which week this exercise belongs to
                day_data = exercise.get("_day_data", {})
                week_id = day_data.get("week_id")

                if week_id:
                    # Initialize week if not yet tracked
                    if week_id not in weekly_volumes:
                        weekly_volumes[week_id] = 0.0

                    # Only process completed exercises
                    if exercise.get("status") == "completed":
                        exercise_volume = self._calculate_exercise_volume(exercise)

                        if exercise_volume > 0:
                            # Add to total volume
                            total_volume += exercise_volume

                            # Add to weekly volume
                            weekly_volumes[week_id] += exercise_volume

                            # Add to exercise type volume
                            exercise_type = exercise.get("exercise_type")
                            if exercise_type:
                                if exercise_type not in exercise_volumes:
                                    exercise_volumes[exercise_type] = 0.0
                                exercise_volumes[exercise_type] += exercise_volume

            # Create week details with week numbers
            week_details = {}
            for week in weeks:
                week_id = week.get("week_id")
                if week_id and week_id in weekly_volumes:
                    week_details[week_id] = {
                        "week_number": week.get("week_number", 0),
                        "volume": weekly_volumes[week_id],
                    }

            result = {
                "block_id": block_id,
                "block_title": block_data.get("title", ""),
                "total_volume": total_volume,
                "weekly_volumes": week_details,
                "exercise_volumes": exercise_volumes,
                "start_date": start_date,
                "end_date": end_date,
            }

            return result

        except Exception as e:
            print(f"Error in calculate_block_volume: {e}")
            return {"error": f"Failed to calculate block volume: {str(e)}"}

    def compare_blocks(self, block_id1: str, block_id2: str) -> Dict[str, Any]:
        """
        Compare training volume and progress between two training blocks

        :param block_id1: The ID of the first training block
        :param block_id2: The ID of the second training block
        :return: A dictionary containing the comparison results
        """
        if not block_id1 or not block_id2:
            return {"error": "Both block IDs are required"}

        try:
            # Get volume analysis for both blocks
            block1_analysis = self.calculate_block_volume(block_id1)
            block2_analysis = self.calculate_block_volume(block_id2)

            # Check for errors in block analysis
            if "error" in block1_analysis or "error" in block2_analysis:
                return {
                    "error": "One or both blocks could not be analyzed",
                    "block1_error": block1_analysis.get("error"),
                    "block2_error": block2_analysis.get("error"),
                }

            # Calculate total volume change
            total_volume1 = block1_analysis.get("total_volume", 0)
            total_volume2 = block2_analysis.get("total_volume", 0)

            volume_diff = total_volume2 - total_volume1
            volume_percent_change = (
                (volume_diff / total_volume1 * 100) if total_volume1 > 0 else 0
            )

            # Compare exercise volumes
            exercise_comparison = {}
            exercise_volumes1 = block1_analysis.get("exercise_volumes", {})
            exercise_volumes2 = block2_analysis.get("exercise_volumes", {})

            all_exercises = set(
                list(exercise_volumes1.keys()) + list(exercise_volumes2.keys())
            )

            for exercise_type in all_exercises:
                vol1 = exercise_volumes1.get(exercise_type, 0)
                vol2 = exercise_volumes2.get(exercise_type, 0)
                diff = vol2 - vol1
                percent_change = (
                    (diff / vol1 * 100) if vol1 > 0 else (100 if vol2 > 0 else 0)
                )

                exercise_comparison[exercise_type] = {
                    "block1_volume": vol1,
                    "block2_volume": vol2,
                    "difference": diff,
                    "percent_change": round(percent_change, 1),
                }

            return {
                "block1": {
                    "id": block_id1,
                    "title": block1_analysis.get("block_title", ""),
                    "total_volume": total_volume1,
                },
                "block2": {
                    "id": block_id2,
                    "title": block2_analysis.get("block_title", ""),
                    "total_volume": total_volume2,
                },
                "comparison": {
                    "volume_difference": volume_diff,
                    "volume_percent_change": round(volume_percent_change, 1),
                    "exercise_comparison": exercise_comparison,
                },
            }

        except Exception as e:
            print(f"Error in compare_blocks: {e}")
            return {"error": f"Failed to compare blocks: {str(e)}"}
