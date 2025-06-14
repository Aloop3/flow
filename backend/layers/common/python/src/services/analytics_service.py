from typing import List, Dict, Any, Optional, Union
from src.repositories.workout_repository import WorkoutRepository
from src.repositories.exercise_repository import ExerciseRepository
from src.repositories.block_repository import BlockRepository
from src.repositories.week_repository import WeekRepository
from src.repositories.day_repository import DayRepository
import datetime as dt


class AnalyticsService:
    def __init__(self):
        self.workout_repository: WorkoutRepository = WorkoutRepository()
        self.exercise_repository: ExerciseRepository = ExerciseRepository()
        self.block_repository: BlockRepository = BlockRepository()
        self.week_repository: WeekRepository = WeekRepository()
        self.day_repository: DayRepository = DayRepository()

    def get_max_weight_history(
        self, athlete_id: str, exercise_type: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the historical maximum weights lifted for a specific exercise type

        :param athlete_id: The ID of the athlete
        :param exercise_type: The type of exercise (e.g., 'squat', 'bench', 'deadlift')
        :return: A list of dictionaries containing the historical maximum weights
        """
        if not athlete_id or not exercise_type:
            return []

        try:
            # Get all exercises of this type for the athlete from workout repository
            exercises = self.workout_repository.get_exercises_by_type(
                athlete_id, exercise_type
            )

            # Filter for completed exercises only
            completed_exercises = [
                exercise
                for exercise in exercises
                if exercise.get("status") == "completed"
                and exercise.get("workout_status") == "completed"
            ]

            # Group exercises by date and find the maximum weight for each day
            max_weight_by_date = {}

            for exercise in completed_exercises:
                date = exercise.get("date")
                weight = exercise.get("weight")

                if date and weight is not None:
                    # Update the max weight for this date if it is higher
                    if (
                        date not in max_weight_by_date
                        or weight > max_weight_by_date[date]
                    ):
                        max_weight_by_date[date] = weight

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
        Volume = sets * reps * weight

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

            # Retrieve completed workouts for the specified time period
            completed_workouts = self.workout_repository.get_completed_workouts_since(
                athlete_id, start_date
            )

            # Calculate volume for each day
            volume_data = {}

            for workout in completed_workouts:
                date = workout.get("date")
                if not date:
                    continue

                daily_volume = 0.0

                # Sum up the volume for each exercise in the workout
                for exercise in workout.get("exercises", []):
                    # Only count completed exercises
                    if exercise.get("status") == "completed":
                        sets = exercise.get("sets")
                        reps = exercise.get("reps")
                        weight = exercise.get("weight")

                        if all(val is not None for val in [sets, reps, weight]):
                            try:
                                exercise_volume = (
                                    float(sets) * float(reps) * float(weight)
                                )
                                daily_volume += exercise_volume
                            except (ValueError, TypeError):
                                # Skip exercises with invalid numeric data
                                continue

                # Store the total daily volume
                if date in volume_data:
                    volume_data[date] += daily_volume
                else:
                    volume_data[date] = daily_volume

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

            # Get all workouts for these days
            all_workouts = []
            for day in all_days:
                day_id = day.get("day_id")
                if day_id:
                    workout_data = self.workout_repository.get_workout_by_day(
                        athlete_id, day_id
                    )
                    if workout_data:
                        # Add day info to workout for later reference
                        workout_data["_day_data"] = day
                        all_workouts.append(workout_data)

            # Calculate total block volume
            total_volume = 0.0
            exercise_volumes = {}
            weekly_volumes = {}

            for workout in all_workouts:
                # Find which week this workout belongs to
                day_data = workout.get("_day_data", {})
                week_id = day_data.get("week_id")

                if week_id:
                    # Initialize week if not yet tracked
                    if week_id not in weekly_volumes:
                        weekly_volumes[week_id] = 0.0

                    # Only process completed workouts
                    if workout.get("status") == "completed":
                        for exercise in workout.get("exercises", []):
                            # Only count completed exercises
                            if exercise.get("status") == "completed":
                                sets = exercise.get("sets")
                                reps = exercise.get("reps")
                                weight = exercise.get("weight")

                                if all(val is not None for val in [sets, reps, weight]):
                                    try:
                                        # Calculate exercise volume
                                        exercise_volume = (
                                            float(sets) * float(reps) * float(weight)
                                        )

                                        # Add to total volume
                                        total_volume += exercise_volume

                                        # Add to weekly volume
                                        weekly_volumes[week_id] += exercise_volume

                                        # Add to exercise type volume
                                        exercise_type = exercise.get("exercise_type")
                                        if exercise_type:
                                            if exercise_type not in exercise_volumes:
                                                exercise_volumes[exercise_type] = 0.0
                                            exercise_volumes[
                                                exercise_type
                                            ] += exercise_volume

                                    except (ValueError, TypeError):
                                        # Skip exercises with invalid numeric data
                                        continue

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

    def get_exercise_frequency(
        self, athlete_id: str, exercise_type: str, time_period: str = "month"
    ) -> Dict[str, Any]:
        """
        Calculate how often a specific exercise is performed over time

        :param athlete_id: The ID of the athlete
        :param exercise_type: The type of exercise to analyze
        :param time_period: The time period for analysis ('week', 'month', 'year')
        :return: Frequency data for the exercise
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

            # Get all exercises of this type for the athlete
            exercises = self.workout_repository.get_exercises_by_type(
                athlete_id, exercise_type
            )

            # Filter by date range and completed status
            filtered_exercises = []
            for exercise in exercises:
                exercise_date = exercise.get("date")
                if (
                    exercise_date
                    and exercise_date >= start_date
                    and exercise.get("status") == "completed"
                    and exercise.get("workout_status") == "completed"
                ):
                    filtered_exercises.append(exercise)

            # Count unique training days
            training_dates = set()
            total_sets = 0

            for exercise in filtered_exercises:
                date = exercise.get("date")
                if date:
                    training_dates.add(date)

                sets = exercise.get("sets")
                if sets is not None:
                    try:
                        total_sets += int(sets)
                    except (ValueError, TypeError):
                        continue

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
