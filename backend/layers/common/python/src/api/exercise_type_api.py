import logging
from src.models.exercise_type import ExerciseType, ExerciseCategory
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors
from src.services.user_service import UserService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

user_service = UserService()


@with_middleware([log_request, handle_errors])
def get_exercise_types(event, context):
    """
    Handle GET /exercise-types request to return exercise library
    Optionally includes user's custom exercises if user_id provided
    """
    try:
        # Get query parameters
        query_params = event.get("queryStringParameters") or {}
        user_id = query_params.get("user_id")

        # Build exercise library with string keys (matching original API structure)
        exercise_library = {}
        all_exercises = []

        # Get predefined exercises by category
        for category in ExerciseType.get_categories():
            if category != ExerciseCategory.CUSTOM:  # Skip CUSTOM category
                category_name = category.value  # Use lowercase string value
                category_exercises = ExerciseType.get_by_category(category)
                exercise_library[category_name] = category_exercises
                all_exercises.extend(category_exercises)

        # Add "all" category with all predefined exercises
        exercise_library["all"] = all_exercises

        # If user_id provided, merge in custom exercises
        if user_id:
            try:
                # Get user and their custom exercises
                user = user_service.get_user(user_id)
                if user and user.custom_exercises:
                    # Group custom exercises by category
                    for custom_exercise in user.custom_exercises:
                        category_name = custom_exercise.get("category", "").lower()
                        exercise_name = custom_exercise.get("name", "")

                        if category_name and exercise_name:
                            # Convert enum name back to lowercase for API consistency
                            if category_name in [
                                "BARBELL",
                                "DUMBBELL",
                                "BODYWEIGHT",
                                "MACHINE",
                                "CABLE",
                            ]:
                                category_name = category_name.lower()

                            # Add to appropriate category
                            if category_name not in exercise_library:
                                exercise_library[category_name] = []
                            exercise_library[category_name].append(exercise_name)

                            # Also add to "all" category
                            exercise_library["all"].append(exercise_name)

            except Exception as e:
                # Log error but continue with predefined exercises only
                logger.warning(
                    f"Failed to load custom exercises for user {user_id}: {str(e)}"
                )

        return create_response(200, exercise_library)

    except Exception as e:
        logger.error(f"Error getting exercise types: {str(e)}")
        return create_response(500, {"error": str(e)})
