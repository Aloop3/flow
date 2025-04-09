import pytest
from unittest.mock import patch, MagicMock
from src.lambdas.cognito_triggers.post_confirmation_lambda import handler


@pytest.fixture
def cognito_event():
    """Create a mock Cognito post confirmation event."""
    return {
        "version": "1",
        "region": "us-east-1",
        "userPoolId": "us-east-1_example",
        "userName": "test-user",
        "callerContext": {"awsSdkVersion": "aws-sdk-version", "clientId": "client-id"},
        "triggerSource": "PostConfirmation_ConfirmSignUp",
        "request": {
            "userAttributes": {
                "sub": "user-id-12345",
                "email": "test@example.com",
                "name": "Test User",
            }
        },
        "response": {},
    }


@pytest.fixture
def cognito_event_no_name():
    """Create a mock Cognito event without name attribute."""
    return {
        "version": "1",
        "region": "us-east-1",
        "userPoolId": "us-east-1_example",
        "userName": "test-user",
        "callerContext": {"awsSdkVersion": "aws-sdk-version", "clientId": "client-id"},
        "triggerSource": "PostConfirmation_ConfirmSignUp",
        "request": {
            "userAttributes": {"sub": "user-id-12345", "email": "test@example.com"}
        },
        "response": {},
    }


@patch("src.lambdas.cognito_triggers.post_confirmation_lambda.users_table")
def test_post_confirmation_success(mock_users_table, cognito_event):
    """Test successful user creation in DynamoDB."""
    # Setup mock
    mock_users_table.put_item = MagicMock()

    # Call the handler
    result = handler(cognito_event, {})

    # Verify it returns the event
    assert result == cognito_event

    # Verify it tried to create a user with correct attributes
    mock_users_table.put_item.assert_called_once()
    call_args = mock_users_table.put_item.call_args[1]["Item"]
    assert call_args["user_id"] == "user-id-12345"
    assert call_args["email"] == "test@example.com"
    assert call_args["name"] == "Test User"
    assert call_args["role"] is None


@patch("src.lambdas.cognito_triggers.post_confirmation_lambda.users_table")
def test_post_confirmation_no_name(mock_users_table, cognito_event_no_name):
    """Test user creation when name attribute is missing."""
    # Setup mock
    mock_users_table.put_item = MagicMock()

    # Call the handler
    result = handler(cognito_event_no_name, {})

    # Verify it returns the event
    assert result == cognito_event_no_name

    # Verify it used email as a fallback for name
    mock_users_table.put_item.assert_called_once()
    call_args = mock_users_table.put_item.call_args[1]["Item"]
    assert call_args["name"] == "test"  # First part of test@example.com


@patch("src.lambdas.cognito_triggers.post_confirmation_lambda.users_table")
def test_post_confirmation_exception(mock_users_table, cognito_event):
    """Test that exceptions don't block the Cognito flow."""
    # Setup mock to raise exception
    mock_users_table.put_item.side_effect = Exception("DynamoDB error")

    # Call the handler
    result = handler(cognito_event, {})

    # Verify it still returns the event even after exception
    assert result == cognito_event


@patch("src.lambdas.cognito_triggers.post_confirmation_lambda.users_table")
def test_name_generation_from_email(mock_users_table, cognito_event_no_name):
    """Test that name is generated from email when missing."""
    mock_users_table.put_item = MagicMock()

    # Call handler directly
    handler(cognito_event_no_name, {})

    # Verify the correct item was created
    call_args = mock_users_table.put_item.call_args[1]["Item"]

    # Email is test@example.com, so name should be "test"
    assert call_args["user_id"] == "user-id-12345"
    assert call_args["email"] == "test@example.com"
    assert call_args["name"] == "test"  # Should be the part before @
    assert call_args["role"] is None
