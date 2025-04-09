import os
import json
import boto3
import pytest
from moto import mock_dynamodb
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
os.environ["REGION"] = "us-east-1"


class LambdaContext:
    """
    Mock Lambda context for testing
    """

    def __init__(self):
        self.function_name = "test-function"
        self.aws_request_id = "test-request-123"
        self.function_version = "$LATEST"
        self.memory_limit_in_mb = 128
        self.log_group_name = "/aws/lambda/test-function"
        self.log_stream_name = "2025/03/28/[$LATEST]abcdef123456"
        self.identity = None
        self.client_context = None

    def get_remaining_time_in_millis(self):
        return 15000


class APIGatewayEvent:
    """
    Utility class for creating API Gateway events
    """

    @staticmethod
    def create(
        method="GET",
        path="/",
        path_parameters=None,
        query_parameters=None,
        body=None,
        headers=None,
        auth_claims=None,
    ):
        """
        Create an API Gateway event for testing Lambda handlers

        :param method: HTTP method (GET, POST, etc.)
        :param path: API path
        :param path_parameters: Path parameters
        :param query_parameters: Query string parameters
        :param body: Request body
        :param headers: HTTP headers
        :param auth_claims: Authentication claims to simulate authenticated requests
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


# Mock AWS services
@pytest.fixture(scope="session", autouse=True)
def mock_boto3():
    """Global mock for boto3 resource to prevent real AWS calls"""
    with patch("boto3.resource") as mock:
        yield mock


@pytest.fixture
def mock_dynamodb_table():
    """Simple mock for a DynamoDB table"""
    table = MagicMock()
    return table


# DynamoDB fixtures using moto
@pytest.fixture
def dynamodb():
    """Fixture that provides a mock DynamoDB instance using moto"""
    with mock_dynamodb():
        yield boto3.resource("dynamodb", region_name="us-east-1")


@pytest.fixture(scope="session", autouse=True)
def mock_dynamodb_session():
    """Start moto mocking at the beginning of the test session"""
    with mock_dynamodb():
        yield


@pytest.fixture
def users_table(dynamodb):
    """Fixture that creates and yields the Users table"""
    table = dynamodb.create_table(
        TableName=os.environ["USERS_TABLE"],
        KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "email-index",
                "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            }
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    yield table


@pytest.fixture
def blocks_table(dynamodb):
    """Fixture that creates and yields the Blocks table"""
    table = dynamodb.create_table(
        TableName=os.environ["BLOCKS_TABLE"],
        KeySchema=[{"AttributeName": "block_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "block_id", "AttributeType": "S"},
            {"AttributeName": "athlete_id", "AttributeType": "S"},
            {"AttributeName": "coach_id", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "athlete-index",
                "KeySchema": [{"AttributeName": "athlete_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
            {
                "IndexName": "coach-index",
                "KeySchema": [{"AttributeName": "coach_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    yield table


@pytest.fixture
def weeks_table(dynamodb):
    """Fixture that creates and yields the Weeks table"""
    table = dynamodb.create_table(
        TableName=os.environ["WEEKS_TABLE"],
        KeySchema=[{"AttributeName": "week_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "week_id", "AttributeType": "S"},
            {"AttributeName": "block_id", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "block-index",
                "KeySchema": [{"AttributeName": "block_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            }
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    yield table


@pytest.fixture
def relationships_table(dynamodb):
    """Fixture that creates and yields the Relationships table"""
    table = dynamodb.create_table(
        TableName=os.environ["RELATIONSHIPS_TABLE"],
        KeySchema=[{"AttributeName": "relationship_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "relationship_id", "AttributeType": "S"},
            {"AttributeName": "coach_id", "AttributeType": "S"},
            {"AttributeName": "athlete_id", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "coach-index",
                "KeySchema": [{"AttributeName": "coach_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
            {
                "IndexName": "athlete-index",
                "KeySchema": [{"AttributeName": "athlete_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
            {
                "IndexName": "coach-athlete-index",
                "KeySchema": [
                    {"AttributeName": "coach_id", "KeyType": "HASH"},
                    {"AttributeName": "athlete_id", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    yield table


# Add fixtures for other tables as needed
@pytest.fixture
def days_table(dynamodb):
    """Fixture that creates and yields the Days table"""
    table = dynamodb.create_table(
        TableName=os.environ["DAYS_TABLE"],
        KeySchema=[{"AttributeName": "day_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "day_id", "AttributeType": "S"},
            {"AttributeName": "week_id", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "week-index",
                "KeySchema": [{"AttributeName": "week_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            }
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    yield table


@pytest.fixture
def workouts_table(dynamodb):
    """Fixture that creates and yields the Workouts table"""
    table = dynamodb.create_table(
        TableName=os.environ["WORKOUTS_TABLE"],
        KeySchema=[{"AttributeName": "workout_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "workout_id", "AttributeType": "S"},
            {"AttributeName": "athlete_id", "AttributeType": "S"},
            {"AttributeName": "day_id", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "athlete-index",
                "KeySchema": [{"AttributeName": "athlete_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
            {
                "IndexName": "day-index",
                "KeySchema": [{"AttributeName": "day_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    yield table


@pytest.fixture
def sets_table(dynamodb):
    """Fixture that creates and yields the Sets table"""
    table = dynamodb.create_table(
        TableName=os.environ["SETS_TABLE"],
        KeySchema=[{"AttributeName": "set_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "set_id", "AttributeType": "S"},
            {"AttributeName": "completed_exercise_id", "AttributeType": "S"},
            {"AttributeName": "workout_id", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "exercise-index",
                "KeySchema": [
                    {"AttributeName": "completed_exercise_id", "KeyType": "HASH"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
            {
                "IndexName": "workout-index",
                "KeySchema": [{"AttributeName": "workout_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    yield table
