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

        # Verify ownership: only the coach can create a relationship
        caller_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if caller_id != coach_id:
            return create_response(
                403, {"error": "Unauthorized to create relationship for this coach"}
            )

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

        # Verify ownership: only the athlete can accept
        caller_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        existing = relationship_service.get_relationship(relationship_id)
        if not existing:
            return create_response(
                404, {"error": "Relationship not found or already accepted"}
            )
        if caller_id != existing.athlete_id:
            return create_response(
                403, {"error": "Unauthorized to accept this relationship"}
            )

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

        # Verify ownership: only the coach or athlete can end
        caller_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        existing = relationship_service.get_relationship(relationship_id)
        if not existing:
            return create_response(
                404, {"error": "Relationship not found or already ended"}
            )
        if caller_id != existing.coach_id and caller_id != existing.athlete_id:
            return create_response(
                403, {"error": "Unauthorized to end this relationship"}
            )

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

        # Verify ownership: only the coach can view their relationships
        caller_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if caller_id != coach_id:
            return create_response(
                403, {"error": "Unauthorized to view relationships for this coach"}
            )

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
def get_relationships_for_athlete(event, context):
    """
    Handle GET /athletes/{athlete_id}/relationships request to get all relationships for an athlete
    """
    try:
        # Extract athlete_id from path parameters
        athlete_id = event["pathParameters"]["athlete_id"]

        # Verify ownership: only the athlete can view their relationships
        caller_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if caller_id != athlete_id:
            return create_response(
                403,
                {"error": "Unauthorized to view relationships for this athlete"},
            )

        # Get query parameter for status filter
        query_params = event.get("queryStringParameters", {}) or {}
        status = query_params.get("status")

        # Get relationships
        relationships = relationship_service.get_relationships_for_athlete(
            athlete_id, status
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

        # Verify ownership: only the coach or athlete can view
        caller_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if caller_id != relationship.coach_id and caller_id != relationship.athlete_id:
            return create_response(
                403, {"error": "Unauthorized to view this relationship"}
            )

        return create_response(200, relationship.to_dict())

    except Exception as e:
        logger.error(f"Error getting relationship: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def generate_invitation_code(event, context):
    """
    Handle POST /coaches/{coach_id}/invitation request to generate invitation code
    """
    try:
        # Extract coach_id from path parameters
        coach_id = event["pathParameters"]["coach_id"]

        # Verify ownership: only the coach can generate invitation codes
        caller_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if caller_id != coach_id:
            return create_response(
                403, {"error": "Unauthorized to generate invitation for this coach"}
            )

        # Generate invitation code
        relationship = relationship_service.generate_invitation_code(coach_id)

        # Return code and expiration info
        response_data = {
            "invitation_code": relationship.invitation_code,
            "expires_at": relationship.ttl,
            "relationship_id": relationship.relationship_id,
        }

        return create_response(201, response_data)
    except Exception as e:
        logger.error(f"Error generating invitation code: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def accept_invitation_code(event, context):
    """
    Handle POST /athletes/{athlete_id}/accept-invitation request to accept an invitation code
    """
    try:
        # Extract athlete_id from path parameters
        athlete_id = event["pathParameters"]["athlete_id"]

        # Verify ownership: only the athlete can accept invitations for themselves
        caller_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if caller_id != athlete_id:
            return create_response(
                403, {"error": "Unauthorized to accept invitation for this athlete"}
            )

        body = json.loads(event["body"])

        # Extract invitation code from body
        invitation_code = body.get("invitation_code")
        if not invitation_code:
            return create_response(400, {"error": "Missing invitation code"})

        # Validate and accept the invitation
        relationship = relationship_service.validate_invitation_code(
            invitation_code, athlete_id
        )

        if not relationship:
            return create_response(404, {"error": "Invalid or expired invitation code"})

        return create_response(200, relationship.to_dict())
    except ValueError as e:
        # Handle existing relationship error
        return create_response(400, {"error": str(e)})
    except Exception as e:
        logger.error(f"Error accepting invitation: {str(e)}")
        return create_response(500, {"error": str(e)})
