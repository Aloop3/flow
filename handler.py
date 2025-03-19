import json
import logging
from src.api import user, block, week, day, exercise, workout, relationship
from src.utils.response import create_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Router configuration mapping API paths to their handlers
ROUTE_CONFIG = {
    # User routes
    "POST /users": user.create_user,
    "GET /users/{user_id}": user.get_user,
    "PUT /users/{user_id}": user.update_user,
    
    # Block routes
    "POST /blocks": block.create_block,
    "GET /blocks/{block_id}": block.get_block,
    "GET /athletes/{athlete_id}/blocks": block.get_blocks_by_athlete,
    "PUT /blocks/{block_id}": block.update_block,
    "DELETE /blocks/{block_id}": block.delete_block,
    
    # Week routes
    "POST /weeks": week.create_week,
    "GET /blocks/{block_id}/weeks": week.get_weeks_for_block,
    "PUT /weeks/{week_id}": week.update_week,
    "DELETE /weeks/{week_id}": week.delete_week,
    
    # Day routes
    "POST /days": day.create_day,
    "GET /weeks/{week_id}/days": day.get_days_for_week,
    "PUT /days/{day_id}": day.update_day,
    "DELETE /days/{day_id}": day.delete_day,
    
    # Exercise routes
    "POST /exercises": exercise.create_exercise,
    "GET /days/{day_id}/exercises": exercise.get_exercises_for_day,
    "PUT /exercises/{exercise_id}": exercise.update_exercise,
    "DELETE /exercises/{exercise_id}": exercise.delete_exercise,
    "POST /exercises/reorder": exercise.reorder_exercises,
    
    # Workout routes
    "POST /workouts": workout.create_workout,
    "GET /workouts/{workout_id}": workout.get_workout,
    "GET /athletes/{athlete_id}/workouts": workout.get_workouts_by_athlete,
    "PUT /workouts/{workout_id}": workout.update_workout,
    "DELETE /workouts/{workout_id}": workout.delete_workout,
    
    # Relationship routes
    "POST /relationships": relationship.create_relationship,
    "POST /relationships/{relationship_id}/accept": relationship.accept_relationship,
    "POST /relationships/{relationship_id}/end": relationship.end_relationship,
    "GET /coaches/{coach_id}/relationships": relationship.get_relationships_for_coach,
    
    # Analytics routes
    # "GET /analytics/athletes/{athlete_id}/max-weight": analytics.get_max_weight_history,
    # "GET /analytics/athletes/{athlete_id}/volume": analytics.calculate_volume,
    # "GET /analytics/blocks/{block_id}/volume": analytics.calculate_block_volume,
    # "GET /analytics/blocks/compare": analytics.compare_blocks
}

def get_route_key(method, path):
    """
    Construct a route key from HTTP method and path
    """
    return f"{method} {path}"

def replace_path_parameters(path_template, path_parameters):
    """
    Replace path parameters in a template with actual values
    """
    result = path_template
    for param_name, param_value in path_parameters.items():
        result = result.replace(f"{{{param_name}}}", param_value)
    return result

def find_handler(method, path, resource_path, path_parameters):
    """
    Find the appropriate handler for a given method and path
    """
    # First, try exact match with full path
    exact_route_key = f"{method} {path}"
    if exact_route_key in ROUTE_CONFIG:
        return ROUTE_CONFIG[exact_route_key]
    
    # Try match with resource path
    resource_route_key = f"{method} {resource_path}"
    if resource_route_key in ROUTE_CONFIG:
        return ROUTE_CONFIG[resource_route_key]
    
    # Try matching routes with path parameters
    for template, handler in ROUTE_CONFIG.items():
        template_method, template_path = template.split(" ", 1)
        
        # Check method first
        if method != template_method:
            continue
        
        # Split paths into parts
        template_parts = template_path.split("/")
        path_parts = path.split("/")
        
        # Check if number of parts match
        if len(template_parts) != len(path_parts):
            continue
        
        # Check if the path matches the template
        match = all(
            template_part.startswith("{") and template_part.endswith("}") or 
            template_part == path_part 
            for template_part, path_part in zip(template_parts, path_parts)
        )
        
        if match:
            return handler
    
    return None

def lambda_handler(event, context):
    """
    Main Lambda handler that receives all API Gateway requests and routes them 
    to the appropriate function
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Extract request details from the API Gateway event
    http_method = event["httpMethod"]
    resource_path = event["resource"]  # e.g., "/users/{user_id}"
    path = event["path"]  # e.g., "/users/123"
    
    # Log the request details
    logger.info(f"Processing {http_method} request to {path}")
    
    # Find the appropriate handler for this request
    path_parameters = event.get("pathParameters", {}) or {}
    
    # Add debugging
    print(f"Looking for handler for: {http_method} {resource_path}")
    print(f"Available routes: {list(ROUTE_CONFIG.keys())}")
    
    # Find the handler for this route
    handler_function = find_handler(http_method, path, resource_path, path_parameters)
    
    print(f"Found handler: {handler_function}")
    
    if not handler_function:
        logger.error(f"No handler found for {http_method} {resource_path}")
        return create_response(404, {"error": "Not Found"})
    
    try:
        # Call the handler function with the API Gateway event and Lambda context
        return handler_function(event, context)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_response(500, {"error": f"Internal server error: {str(e)}"})