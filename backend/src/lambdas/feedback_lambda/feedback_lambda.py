import json
import logging
import boto3
import os
from datetime import datetime as dt, timezone
from src.utils.cors_utils import add_cors_headers

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client("sns")


def add_feedback_cors_headers(response):
    """Add proper CORS headers for feedback endpoint"""
    if "headers" not in response:
        response["headers"] = {}

    response["headers"].update(
        {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
        }
    )
    return response


def handler(event, context):
    """
    Lambda handler for beta feedback collection
    Sends feedback via SNS to monitoring email
    """
    # Handle OPTIONS request for CORS
    if event.get("httpMethod") == "OPTIONS":
        return add_feedback_cors_headers(
            {"statusCode": 200, "body": json.dumps({"message": "OK"})}
        )

    try:
        # Basic auth check
        try:
            request_context = event.get("requestContext")
            if not request_context:
                logger.error("requestContext is missing")
                return add_feedback_cors_headers(
                    {
                        "statusCode": 401,
                        "body": json.dumps(
                            {"error": "Unauthorized - no request context"}
                        ),
                    }
                )

            authorizer = (
                request_context.get("authorizer")
                if hasattr(request_context, "get")
                else None
            )
            if not authorizer:
                logger.error("authorizer is missing")
                return add_cors_headers(
                    {
                        "statusCode": 401,
                        "body": json.dumps({"error": "Unauthorized - no authorizer"}),
                    }
                )

            claims = authorizer.get("claims") if hasattr(authorizer, "get") else None
            if not claims:
                logger.error("claims is missing")
                return add_cors_headers(
                    {
                        "statusCode": 401,
                        "body": json.dumps({"error": "Unauthorized - no claims"}),
                    }
                )

        except Exception as auth_error:
            logger.error(f"Auth check failed: {str(auth_error)}")
            return add_cors_headers(
                {
                    "statusCode": 401,
                    "body": json.dumps({"error": "Unauthorized - auth error"}),
                }
            )

        # Parse request body
        try:
            body_raw = event.get("body")
            if not body_raw:
                return add_cors_headers(
                    {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Request body is required"}),
                    }
                )

            # Handle both string and dict bodies
            if isinstance(body_raw, str):
                body = json.loads(body_raw)
                # Check if we got a string back (double-encoded JSON)
                if isinstance(body, str):
                    body = json.loads(body)
            elif isinstance(body_raw, dict):
                body = body_raw
            else:
                logger.error(f"Unexpected body type: {type(body_raw)}")
                return add_cors_headers(
                    {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Invalid body format"}),
                    }
                )

        except json.JSONDecodeError as json_error:
            logger.error(f"JSON decode error: {str(json_error)}")
            return add_cors_headers(
                {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid JSON in request body"}),
                }
            )
        except Exception as body_error:
            logger.error(f"Body parsing error: {str(body_error)}")
            return add_cors_headers(
                {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Body parsing failed"}),
                }
            )

        # Validate required fields
        try:
            required_fields = ["category", "message"]
            for field in required_fields:
                if not hasattr(body, "get"):
                    logger.error(f"body is not dict-like, type: {type(body)}")
                    return add_cors_headers(
                        {
                            "statusCode": 400,
                            "body": json.dumps({"error": "Invalid body structure"}),
                        }
                    )

                if not body.get(field):
                    return add_cors_headers(
                        {
                            "statusCode": 400,
                            "body": json.dumps(
                                {"error": f"Missing required field: {field}"}
                            ),
                        }
                    )

        except Exception as validation_error:
            logger.error(f"Field validation error: {str(validation_error)}")
            return add_cors_headers(
                {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Field validation failed"}),
                }
            )

        # Extract user info
        try:
            user_email = (
                claims.get("email", "unknown") if hasattr(claims, "get") else "unknown"
            )
            user_name = (
                claims.get(
                    "name",
                    user_email.split("@")[0] if "@" in str(user_email) else "unknown",
                )
                if hasattr(claims, "get")
                else "unknown"
            )
            user_id = (
                claims.get("sub", "unknown") if hasattr(claims, "get") else "unknown"
            )
        except Exception as user_error:
            logger.error(f"User info extraction error: {str(user_error)}")
            user_email = user_name = user_id = "unknown"

        # Get feedback data
        try:
            category = (
                body.get("category", "unknown") if hasattr(body, "get") else "unknown"
            )
            message = (
                body.get("message", "No message provided")
                if hasattr(body, "get")
                else "No message provided"
            )
            page_url = (
                body.get("pageUrl", "Not provided")
                if hasattr(body, "get")
                else "Not provided"
            )
        except Exception as data_error:
            logger.error(f"Data extraction error: {str(data_error)}")
            category = message = page_url = "unknown"

        # Extract User-Agent header
        try:
            headers = event.get("headers", {})
            user_agent = "Not provided"
            if hasattr(headers, "get"):
                user_agent = headers.get("User-Agent", "Not provided")
        except Exception as header_error:
            logger.error(f"Header extraction error: {str(header_error)}")
            user_agent = "Not provided"

        timestamp = dt.now(timezone.utc).isoformat()

        # Validate category
        valid_categories = ["bug", "suggestion", "question", "feature-request"]
        if category not in valid_categories:
            return add_cors_headers(
                {
                    "statusCode": 400,
                    "body": json.dumps(
                        {
                            "error": f'Invalid category. Must be one of: {", ".join(valid_categories)}'
                        }
                    ),
                }
            )

        # Format email content
        subject = f"[FLOW BETA] {category.upper()}: {message[:50]}..."

        email_body = f"""
🚀 FLOW Beta Feedback - {category.upper()}

👤 USER DETAILS:
• Name: {user_name}
• Email: {user_email}
• User ID: {user_id}
• Timestamp: {timestamp}

📝 FEEDBACK:
{message}

🔗 CONTEXT:
• Page URL: {page_url}
• User Agent: {user_agent}

---
This feedback was submitted via the Flow Beta feedback widget.
        """.strip()

        # Send feedback via SNS
        environment = os.environ.get("ENVIRONMENT", "dev")

        try:
            # Get AWS account ID from context
            account_id = context.invoked_function_arn.split(":")[4]
            region = os.environ.get("REGION", "us-east-1")

            # Choose appropriate SNS topic
            if environment == "dev":
                topic_arn = f"arn:aws:sns:{region}:{account_id}:flow-{environment}-feedback-alerts"
            else:
                topic_arn = f"arn:aws:sns:{region}:{account_id}:flow-{environment}-monitoring-alerts"

            # Send feedback via SNS
            response = sns.publish(
                TopicArn=topic_arn, Subject=subject, Message=email_body
            )

            logger.info(
                f"Feedback sent successfully. MessageId: {response['MessageId']}"
            )

            return add_feedback_cors_headers(
                {
                    "statusCode": 200,
                    "body": json.dumps(
                        {
                            "message": "Feedback submitted successfully",
                            "feedback_id": response["MessageId"],
                        }
                    ),
                }
            )

        except Exception as sns_error:
            # If SNS fails, log the feedback and return success
            logger.warning(f"SNS publish failed: {str(sns_error)}")
            logger.info(f"FEEDBACK LOGGED: {subject}\n{email_body}")

            return add_feedback_cors_headers(
                {
                    "statusCode": 200,
                    "body": json.dumps(
                        {
                            "message": "Feedback submitted successfully (logged)",
                            "feedback_id": f"logged-{timestamp}",
                        }
                    ),
                }
            )

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return add_feedback_cors_headers(
            {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON in request body"}),
            }
        )

    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return add_feedback_cors_headers(
            {"statusCode": 500, "body": json.dumps({"error": "Internal server error"})}
        )
