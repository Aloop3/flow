import unittest
import os
import json
from unittest.mock import patch, MagicMock

# Set test environment variables
os.environ["USERS_TABLE"] = "Users-Test"
os.environ["BLOCKS_TABLE"] = "Blocks-Test"
os.environ["WEEKS_TABLE"] = "Weeks-Test"
os.environ["DAYS_TABLE"] = "Days-Test"
os.environ["EXERCISES_TABLE"] = "Exercises-Test"
os.environ["WORKOUTS_TABLE"] = "Workouts-Test"
os.environ["COMPLETED_EXERCISES_TABLE"] = "CompletedExercises-Test"
os.environ["RELATIONSHIPS_TABLE"] = "Relationships-Test"
os.environ["SETS_TABLE"] = "Sets-Test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

class BaseTest(unittest.TestCase):
    """Base test class that handles setting up mocks for DynamoDB and other AWS services."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests in the class."""
        # Create a mock table to return from DynamoDB resource
        cls.mock_table = MagicMock()
        cls.mock_dynamodb = MagicMock()
        cls.mock_dynamodb.Table.return_value = cls.mock_table

        # Start the boto3 patch with our mock
        cls.boto3_patch = patch('boto3.resource', return_value=cls.mock_dynamodb)
        cls.boto3_mock = cls.boto3_patch.start()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests in the class have run."""
        cls.boto3_patch.stop()

    def create_api_gateway_event(
        self,
        method="GET",
        path="/",
        path_parameters=None,
        query_parameters=None,
        body=None,
        headers=None,
        auth_claims=None,
    ):
        """
        Create an API Gateway event object for testing Lambda functions.

        :param method: HTTP method (GET, POST, etc.)
        :param path: API path
        :param path_parameters: Path parameters
        :param query_parameters: Query string parameters
        :param body: Request body (will be converted to JSON)
        :param headers: HTTP headers
        :param auth_claims: Authentication claims
        :return: API Gateway event dictionary
        """
        event = {
            "httpMethod": method,
            "path": path,
            "pathParameters": path_parameters or {},
            "queryStringParameters": query_parameters or {},
            "headers": headers or {},
            "body": json.dumps(body) if body is not None else None,
            "requestContext": {
                "authorizer": {"claims": auth_claims or {}} if auth_claims else {}
            },
        }
        return event

    def create_lambda_context(
        self, function_name="test-function", aws_request_id="test-request-123"
    ):
        """
        Create a mock Lambda context object.

        :param function_name: Name of the Lambda function
        :param aws_request_id: Request ID
        :return: Mock Lambda context object
        """
        context = type(
            "LambdaContext",
            (),
            {
                "function_name": function_name,
                "aws_request_id": aws_request_id,
                "function_version": "$LATEST",
                "memory_limit_in_mb": 128,
                "log_group_name": f"/aws/lambda/{function_name}",
                "log_stream_name": "2025/03/28/[$LATEST]abcdef123456",
                "identity": None,
                "client_context": None,
                "get_remaining_time_in_millis": lambda: 15000,
            },
        )()

        return context
