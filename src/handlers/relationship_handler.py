import json
import logging
from src.services.relationship_service import RelationshipService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

relationship_service = RelationshipService()

def create_relationship(event, context):
    """
    Lambda function to create a new coach-athlete relationship
    """
    try:
        body = json.loads(event["body"])

        # Extract relationship details
        coach_id = body.get("coach_id")
        athlete_id = body.get("athlete_id")

        # Validate required fields
        if not coach_id or not athlete_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }
        
        # Create relationship
        relationship = relationship_service.create_relationship(coach_id, athlete_id)

        return {
            "statusCode": 201,
            "body": json.dumps(relationship.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error creating relationship: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
def accept_relationship(event, context):
    """
    Lambda function to accept a coach-athlete relationship
    """
    try:
        # Extract relationship_id from path parameters
        relationship_id = event["pathParameters"]["relationship_id"]

        # Accept relationship
        accept_relationship = relationship_service.accept_relationship(relationship_id)

        if not accept_relationship:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Relationship not found or already exists"})
            }
        
        return {
            "statusCode": 200,
            "body": json.dumps(accept_relationship.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error accepting relationship: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
def end_relationship(event, context):
    """
    Lambda function to end a coach-athlete relationship
    """
    try:
        # Extract relationship_id from path parameters
        relationship_id = event["pathParameters"]["relationship_id"]

        # End relationship
        end_relationship = relationship_service.end_relationship(relationship_id)

        if not end_relationship:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Relationship not found or already ended"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps(end_relationship.to_dict())
        }

    except Exception as e:
        logger.error(f"Error ending relationship: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def get_relationships_for_coach(event, context):
    """
    Lambda function to get all relationships for a coach
    """
    try:
        # Extract coach_id from path parameters
        coach_id = event["pathParameters"]["coach_id"]

        # Get query parameter for status filter
        query_params = event.get("queryStringParameters", {}) or {}
        status = query_params.get("status")

        # Get relationships
        relationships = relationship_service.get_relationships_for_coach(coach_id, status)

        return {
            "statusCode": 200,
            "body": json.dumps([relationship.to_dict() for relationship in relationships])
        }
    
    except Exception as e:
        logger.error(f"Error getting relationships: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
