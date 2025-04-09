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
        :param exercise_type: The type of exercise
        :return: A list of dictionaries containing the historical maximum weights
        """
        # Retrieve all completed workouts for the athlete
        completed_exercises = self.workout_repository.get_completed_exercises_by_type(
            athlete_id, exercise_type
        )

        # Group exercises by day and find the maximum weight for each day
        max_weight_by_date = {}

        for exercise in completed_exercises:
            # Check if the exercise has weight data
            if exercise.get("actual_weight") and exercise.get("date"):
                date = exercise["date"]
                weight = exercise["actual_weight"]

                # Update the max weight for this date if it is higher
                if date not in max_weight_by_date or weight > max_weight_by_date[date]:
                    max_weight_by_date[date] = weight

        # Convert ditionary to list of data points
        max_weight_data = [
            {"date": date, "max_weight": weight}
            for date, weight in max_weight_by_date.items()
        ]

        # Sort the data points chronologically
        max_weight_data.sort(key=lambda x: x["date"])

        return max_weight_data

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
        # Get start date base on time period
        now = dt.datetime.now()

        if time_period == "week":
            start_date = (now - dt.timedelta(days=7)).isoformat()
        elif time_period == "month":
            start_date = (now - dt.timedelta(days=30)).isoformat()
        elif time_period == "year":
            start_date = (now - dt.timedelta(days=365)).isoformat()
        else:
            start_date = "2000-01-01"  # All time

        # Retrieve workouts for the specified time period
        completed_workouts = self.workout_repository.get_completed_workouts_since(
            athlete_id, start_date
        )

        # Calculate volume for each day
        volume_data = {}
        for workout in completed_workouts:
            date = workout["date"]
            daily_volume = 0.0

        # Sum up the volume for each exercise in the workout
        for exercise in workout.get("exercises", []):
            if all(
                k in exercise for k in ["actual_sets", "actual_reps", "actual_weight"]
            ):
                exercise_volume = (
                    exercise["actual_sets"]
                    * exercise["actual_reps"]
                    * exercise["actual_weight"]
                )
                daily_volume += exercise_volume

        # Store the total daily volume
        volume_data[date] = daily_volume

        # Convert to list of dicts for easier consumption by frontend
        result = [
            {"date": date, "volume": volume} for date, volume in volume_data.items()
        ]

        # Sort chronologically
        result.sort(key=lambda x: x["date"])

        return result

    def calculate_block_volume(self, block_id: str) -> Dict[str, Any]:
        """
        Calculate total and weekly training volume for a specific training block

        :param block_id: The ID of the training block
        :return: A dictionary containing the total volume, weekly volumes, and exercise breakdowns
        """
        # Get the block data to detemine athlete and time period
        block_data = self.block_repository.get_block(block_id)

        if not block_data:
            return {"error": "Block not found"}

        athlete_id = block_data["athlete_id"]
        start_date = block_data["start_date"]
        end_date = block_data["end_date"]

        # Get all weeks in a block
        weeks = self.week_repository.get_weeks_by_block(block_id)

        # Get all days associated with the block
        all_days = []

        for week in weeks:
            week_id = week["week_id"]
            days = self.day_repository.get_days_by_week(week_id)
            all_days.extend(days)

        # Get all day IDs from the block
        day_ids = [day["day_id"] for day in all_days]

        # Get all workouts for these days
        all_workouts = []

        for day_id in day_ids:
            workout_data = self.workout_repository.get_workout_by_day(
                athlete_id, day_id
            )

            if workout_data:
                all_workouts.append(workout_data)

        # Calculate total block volume
        total_volume = 0.0
        exercise_volumes = {}
        weekly_volumes = {}

        for workout in all_workouts:
            # Find which week this workout belongs to
            day_id = workout["day_id"]
            day_data = next((day for day in all_days if day["day_id"] == day_id), None)

            if day_data:
                week_id = day_data["week_id"]

                # Initialize week if not yet tracked
                if week_id not in weekly_volumes:
                    weekly_volumes[week_id] = 0.0

                for exercise in workout.get("exercises", []):
                    if all(
                        k in exercise
                        for k in ["actual_sets", "actual_reps", "actual_weight"]
                    ):
                        # Calculate exercise volume
                        exercise_volume: float = (
                            exercise["actual_sets"]
                            * exercise["actual_reps"]
                            * exercise["actual_weight"]
                        )

                        # Add to total volume
                        total_volume += exercise_volume

                        # Add to weekly volume
                        weekly_volumes[week_id] += exercise_volume

                        # Add to exercise type volume
                        if "exercise_type" in exercise:
                            exercise_type = exercise["exercise_type"]
                            if exercise_type not in exercise_volumes:
                                exercise_volumes[exercise_type] = 0.0
                            exercise_volumes[exercise_type] += exercise_volume

        week_details = {}
        for week in weeks:
            week_id = week["week_id"]
            if week_id in weekly_volumes:
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

    def compare_blocks(self, block_id1: str, block_id2: str) -> Dict[str, Any]:
        """
        Compare training volume and progress between two training blocks

        :param block_id1: The ID of the first training block
        :param block_id2: The ID of the second training block
        :return: A dictionary containing the comparison results
        """
        # Get total volume change
        block1_analysis = self.calculate_block_volume(block_id1)
        block2_analysis = self.calculate_block_volume(block_id2)

        # Calculate differences and precent changes
        if "error" in block1_analysis or "error" in block2_analysis:
            return {"error": "One or both blocks not found"}

        # Calculate total volume change
        total_volume1 = block1_analysis["total_volume"]
        total_volume2 = block2_analysis["total_volume"]

        volume_diff = total_volume2 - total_volume1
        volume_percent_change = (
            (volume_diff / total_volume1 * 100) if total_volume1 > 0 else 0
        )

        # Compare exercise volumes
        exercise_comparison = {}
        all_exercises = set(
            list(block1_analysis["exercise_volumes"].keys())
            + list(block2_analysis["exercise_volumes"].keys())
        )

        for exercise_type in all_exercises:
            vol1 = block1_analysis["exercise_volumes"].get(exercise_type, 0)
            vol2 = block2_analysis["exercise_volumes"].get(exercise_type, 0)
            diff = vol2 - vol1
            percent_change = (diff / vol1 * 100) if vol1 > 0 else 0

            exercise_comparison[exercise_type] = {
                "block1_volume": vol1,
                "block2_volume": vol2,
                "difference": diff,
                "percent_change": percent_change,
            }

        return {
            "block1": {
                "id": block_id1,
                "title": block1_analysis["block_title"],
                "total_volume": total_volume1,
            },
            "block2": {
                "id": block_id2,
                "title": block2_analysis["block_title"],
                "total_volume": total_volume2,
            },
            "comparison": {
                "volume_difference": volume_diff,
                "volume_percent_change": round(volume_percent_change, 1),
                "exercise_comparison": exercise_comparison,
            },
        }
