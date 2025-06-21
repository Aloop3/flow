import logging
from datetime import datetime
from src.utils.response import create_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Simple health check endpoint for CI/CD validation.
    Returns 200 with timestamp and environment info.
    No authentication required.
    """
    try:
        # Get current timestamp
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Basic environment validation
        import os

        environment = os.getenv("ENVIRONMENT", "unknown")

        health_data = {
            "status": "healthy",
            "timestamp": timestamp,
            "environment": environment,
            "service": "flow-api",
        }

        logger.info(f"Health check successful for environment: {environment}")
        return create_response(200, health_data)

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return create_response(
            500,
            {
                "status": "unhealthy",
                "error": "Internal server error",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )
