import json
import logging
from src.services.relationship_service import RelationshipService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors

logger = logging.getLogger()
logger.setLevel(logging.INFO)

relationship_service = RelationshipService()


@with_middleware([log_request, handle_errors])
def create_relationship(event, context):
    """
    Handle POST /relationships request to create a new coach-athlete relationship
    """
    try:
        body = json.loads(event["body"])

        # Extract relationship details
        coach_id = body.get("coach_id")
        athlete_id = body.get("athlete_id")

        # Validate required fields
        if not coach_id or not athlete_id:
            return create_response(400, {"error": "Missing required fields"})

        # Create relationship
        relationship = relationship_service.create_relationship(coach_id, athlete_id)

        return create_response(201, relationship.to_dict())

    except Exception as e:
        logger.error(f"Error creating relationship: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def accept_relationship(event, context):
    """
    Handle POST /relationships/{relationship_id}/accept request to accept a coach-athlete relationship
    """
    try:
        # Extract relationship_id from path parameters
        relationship_id = event["pathParameters"]["relationship_id"]

        # Accept relationship
        accept_relationship = relationship_service.accept_relationship(relationship_id)

        if not accept_relationship:
            return create_response(
                404, {"error": "Relationship not found or already accepted"}
            )

        return create_response(200, accept_relationship.to_dict())

    except Exception as e:
        logger.error(f"Error accepting relationship: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def end_relationship(event, context):
    """
    Handle POST /relationships/{relationship_id}/end request to end a coach-athlete relationship
    """
    try:
        # Extract relationship_id from path parameters
        relationship_id = event["pathParameters"]["relationship_id"]

        # End relationship
        end_relationship = relationship_service.end_relationship(relationship_id)

        if not end_relationship:
            return create_response(
                404, {"error": "Relationship not found or already ended"}
            )

        return create_response(200, end_relationship.to_dict())

    except Exception as e:
        logger.error(f"Error ending relationship: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def get_relationships_for_coach(event, context):
    """
    Handle GET /coaches/{coach_id}/relationships request to get all relationships for a coach
    """
    try:
        # Extract coach_id from path parameters
        coach_id = event["pathParameters"]["coach_id"]

        # Get query parameter for status filter
        query_params = event.get("queryStringParameters", {}) or {}
        status = query_params.get("status")

        # Get relationships
        relationships = relationship_service.get_relationships_for_coach(
            coach_id, status
        )

        return create_response(
            200, [relationship.to_dict() for relationship in relationships]
        )

    except Exception as e:
        logger.error(f"Error getting relationships: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def get_relationship(event, context):
    """
    Handle GET /relationships/{relationship_id} request to retrieve a relationship by ID
    """
    try:
        # Extract relationship_id from path parameters
        relationship_id = event["pathParameters"]["relationship_id"]

        # Get relationship
        relationship = relationship_service.get_relationship(relationship_id)

        if not relationship:
            return create_response(404, {"error": "Relationship not found"})

        return create_response(200, relationship.to_dict())

    except Exception as e:
        logger.error(f"Error getting relationship: {str(e)}")
        return create_response(500, {"error": str(e)})
