import logging
from src.models.exercise_type import ExerciseType, ExerciseCategory
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@with_middleware([log_request, handle_errors])
def get_exercise_types(event, context):
    """
    Handle GET /exercises/types request to get all predefined exercise types
    """
    try:
        # Get all exercise categories
        categories = ExerciseType.get_categories()

        # Structure the response as a map of categories to exercises
        result = {}
        for category in categories:
            exercises = ExerciseType.get_by_category(category)
            result[category.value] = exercises

        # Add "all" category containing all exercises
        result["all"] = ExerciseType.get_all_predefined()

        return create_response(200, result)
    except Exception as e:
        logger.error(f"Error retrieving exercise types: {str(e)}")
        return create_response(500, {"error": str(e)})
