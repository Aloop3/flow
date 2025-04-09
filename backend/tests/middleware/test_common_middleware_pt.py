import json
import pytest
from unittest.mock import MagicMock, patch
from src.middleware.middleware import ValidationError
from src.middleware.common_middleware import validate_auth, log_request, handle_errors


@pytest.fixture
def mock_context():
    """Fixture for a Lambda context with an aws_request_id"""
    context = MagicMock()
    context.aws_request_id = "test-request-123"
    return context


# Path parameter requirements mapping from common_middleware.py
PATH_PARAM_REQUIREMENTS = {
    "GET /users/{user_id}": ["user_id"],
    "GET /blocks/{block_id}": ["block_id"],
    "GET /blocks/{block_id}/weeks": ["block_id"],
    "GET /weeks/{week_id}/days": ["week_id"],
    "GET /workouts/{workout_id}": ["workout_id"],
    "PUT /users/{user_id}": ["user_id"],
    "PUT /blocks/{block_id}": ["block_id"],
    "PUT /weeks/{week_id}": ["week_id"],
    "PUT /days/{day_id}": ["day_id"],
    "DELETE /blocks/{block_id}": ["block_id"],
    "DELETE /weeks/{week_id}": ["week_id"],
    "DELETE /days/{day_id}": ["day_id"],
    "DELETE /workouts/{workout_id}": ["workout_id"],
}

# Query parameter requirements mapping from common_middleware.py
QUERY_PARAM_REQUIREMENTS = {
    "GET /coaches/{coach_id}/relationships": ["status"],
    "GET /athletes/{athlete_id}/progress": ["time_period"],
}


def generate_test_cases_for_path_params():
    """Generate test cases for every path parameter endpoint"""
    test_cases = []

    for route, required_params in PATH_PARAM_REQUIREMENTS.items():
        method, path = route.split(" ", 1)

        # Create a real path by replacing parameters with values
        real_path = path
        path_params = {}
        for param in required_params:
            param_placeholder = "{" + param + "}"
            real_path = real_path.replace(param_placeholder, param + "-123")
            path_params[param] = param + "-123"

        test_cases.append(
            {
                "method": method,
                "path": real_path,
                "path_pattern": path,
                "path_params": path_params,
                "required_params": required_params,
            }
        )

    return test_cases


def generate_test_cases_for_query_params():
    """Generate test cases for every query parameter endpoint"""
    test_cases = []

    for route, required_params in QUERY_PARAM_REQUIREMENTS.items():
        method, path = route.split(" ", 1)

        # Create a real path by replacing parameters with values
        real_path = path
        path_params = {}
        for param_placeholder in path.split("/"):
            if param_placeholder.startswith("{") and param_placeholder.endswith("}"):
                param = param_placeholder[1:-1]
                real_path = real_path.replace(param_placeholder, param + "-123")
                path_params[param] = param + "-123"

        # Create query params
        query_params = {param: "test-value" for param in required_params}

        test_cases.append(
            {
                "method": method,
                "path": real_path,
                "path_pattern": path,
                "path_params": path_params,
                "query_params": query_params,
                "required_params": required_params,
            }
        )

    return test_cases


class TestValidateAuth:
    """Tests for the validate_auth middleware function"""

    def test_valid_auth(self):
        """Test validate_auth with valid authentication"""
        event = {"requestContext": {"authorizer": {"claims": {"sub": "user123"}}}}
        context = MagicMock()

        result = validate_auth(event, context)
        assert result == event

    def test_missing_request_context(self):
        """Test validate_auth when requestContext is missing"""
        event = {}  # No requestContext
        context = MagicMock()

        with pytest.raises(ValidationError) as exc:
            validate_auth(event, context)
        assert str(exc.value) == "Unauthorized"

    def test_missing_authorizer(self):
        """Test validate_auth when authorizer is missing"""
        event = {"requestContext": {}}  # No authorizer
        context = MagicMock()

        with pytest.raises(ValidationError) as exc:
            validate_auth(event, context)
        assert str(exc.value) == "Unauthorized"

    def test_missing_claims(self):
        """Test validate_auth when claims are missing"""
        event = {"requestContext": {"authorizer": {}}}  # No claims
        context = MagicMock()

        with pytest.raises(ValidationError) as exc:
            validate_auth(event, context)
        assert str(exc.value) == "Unauthorized"

    def test_validate_auth_success(self):
        """Test validate_auth with valid authentication data"""
        # Setup valid event with all required auth fields
        event = {"requestContext": {"authorizer": {"claims": {"sub": "user123"}}}}
        context = MagicMock()

        # Call function - should not raise an exception
        result = validate_auth(event, context)

        # Verify event is returned unchanged
        assert result == event

    def test_validate_auth_missing_request_context(self):
        """Test validate_auth with missing requestContext"""
        # Setup event with missing requestContext
        event = {}
        context = MagicMock()

        # Call function and verify it raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            validate_auth(event, context)

        assert str(exc_info.value) == "Unauthorized"

    def test_validate_auth_missing_authorizer(self):
        """Test validate_auth with missing authorizer field"""
        # Setup event with requestContext but missing authorizer
        event = {"requestContext": {}}
        context = MagicMock()

        # Call function and verify it raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            validate_auth(event, context)

        assert str(exc_info.value) == "Unauthorized"

    def test_validate_auth_missing_claims(self):
        """Test validate_auth with missing claims field"""
        # Setup event with authorizer but missing claims
        event = {"requestContext": {"authorizer": {}}}
        context = MagicMock()

        # Call function and verify it raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            validate_auth(event, context)

        assert str(exc_info.value) == "Unauthorized"

    def test_validate_auth_logger_called(self):
        """Test that logger.error is called when validation fails"""
        # Setup event that will fail validation
        event = {}
        context = MagicMock()

        # Mock the logger
        with patch("src.middleware.common_middleware.logger") as mock_logger:
            # Call function and catch expected exception
            with pytest.raises(ValidationError):
                validate_auth(event, context)

            # Verify logger was called with expected message
            mock_logger.error.assert_called_once_with("No auth claims found in event")


class TestLogRequest:
    """Tests for the log_request middleware function"""

    def test_with_request_id(self):
        """Test log_request with aws_request_id available"""
        event = {"path": "/test", "httpMethod": "GET"}
        context = MagicMock()
        context.aws_request_id = "request-123"

        with patch("src.middleware.common_middleware.logger") as mock_logger:
            result = log_request(event, context)

            assert result == event
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "request_id=request-123" in log_message
            assert "path=/test" in log_message
            assert "method=GET" in log_message

    def test_without_request_id(self):
        """Test log_request without aws_request_id available"""
        event = {"path": "/test", "httpMethod": "GET"}
        context = MagicMock(spec=[])  # No aws_request_id attribute

        with patch("src.middleware.common_middleware.logger") as mock_logger:
            result = log_request(event, context)

            assert result == event
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "request_id=unknown" in log_message

    def test_with_user(self):
        """Test log_request with user info in context"""
        event = {
            "path": "/test",
            "httpMethod": "GET",
            "requestContext": {"authorizer": {"claims": {"sub": "user123"}}},
        }
        context = MagicMock()

        with patch("src.middleware.common_middleware.logger") as mock_logger:
            result = log_request(event, context)

            assert result == event
            log_message = mock_logger.info.call_args[0][0]
            assert "user=user123" in log_message

    def test_missing_path_method(self):
        """Test log_request with missing path and method"""
        event = {}  # No path or method
        context = MagicMock()

        with patch("src.middleware.common_middleware.logger") as mock_logger:
            result = log_request(event, context)

            assert result == event
            log_message = mock_logger.info.call_args[0][0]
            assert "path=unknown" in log_message
            assert "method=unknown" in log_message

    def test_log_request_with_aws_request_id(self):
        """Test log_request with aws_request_id available"""
        event = {"path": "/test", "httpMethod": "GET"}
        context = MagicMock()
        context.aws_request_id = "test-123"

        with patch("src.middleware.common_middleware.logger") as mock_logger:
            result = log_request(event, context)
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "request_id=test-123" in log_message

    def test_log_request_without_aws_request_id(self):
        """Test log_request without aws_request_id"""
        event = {"path": "/test", "httpMethod": "GET"}
        context = MagicMock(spec=[])  # No aws_request_id

        with patch("src.middleware.common_middleware.logger") as mock_logger:
            result = log_request(event, context)
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "request_id=unknown" in log_message


class TestHandleErrors:
    """Tests for the handle_errors middleware function"""

    def test_valid_event(self):
        """Test handle_errors with a valid event"""
        event = {
            "httpMethod": "GET",
            "path": "/users",
            "body": json.dumps({"key": "value"}),
        }
        context = MagicMock()

        result = handle_errors(event, context)
        assert result == {**event, "errors": []}

    def test_invalid_json(self):
        """Test handle_errors with invalid JSON in body"""
        event = {"body": "{invalid json"}
        context = MagicMock()

        with pytest.raises(ValidationError) as exc:
            handle_errors(event, context)
        assert "Invalid JSON" in str(exc.value)

    def test_missing_path_parameters(self):
        """Test handle_errors with missing path parameters"""
        event = {
            "httpMethod": "GET",
            "path": "/users/123",
            "pathParameters": {},  # Empty path parameters
        }
        context = MagicMock()

        with pytest.raises(ValidationError) as exc:
            handle_errors(event, context)
        assert "Missing path parameter" in str(exc.value)

    def test_null_path_parameters(self):
        """Test handle_errors with null pathParameters"""
        event = {
            "httpMethod": "GET",
            "path": "/users/123",
            "pathParameters": None,  # Null pathParameters
        }
        context = MagicMock()

        with pytest.raises(ValidationError) as exc:
            handle_errors(event, context)
        assert "Missing path parameter" in str(exc.value)

    def test_path_parameter_not_matching_pattern(self):
        """Test handle_errors when path doesn't match pattern"""
        event = {
            "httpMethod": "GET",
            "path": "/custom/path/123",  # Path not in requirements mapping
            "pathParameters": {},
        }
        context = MagicMock()

        result = handle_errors(event, context)
        assert result["errors"] == []

    def test_missing_query_parameters(self):
        """Test handle_errors with missing query parameters"""
        event = {
            "httpMethod": "GET",
            "path": "/athletes/123/progress",
            "pathParameters": {"athlete_id": "123"},
            "queryStringParameters": {},  # Missing time_period
        }
        context = MagicMock()

        result = handle_errors(event, context)
        assert any(
            "Missing query parameter: time_period" in error
            for error in result["errors"]
        )

    def test_null_query_parameters(self):
        """Test handle_errors with null queryStringParameters"""
        event = {
            "httpMethod": "GET",
            "path": "/athletes/123/progress",
            "pathParameters": {"athlete_id": "123"},
            "queryStringParameters": None,  # Null queryStringParameters
        }
        context = MagicMock()

        result = handle_errors(event, context)
        assert any(
            "Missing query parameter: time_period" in error
            for error in result["errors"]
        )

    def test_query_parameter_not_matching_pattern(self):
        """Test handle_errors when path doesn't match query param pattern"""
        event = {
            "httpMethod": "GET",
            "path": "/custom/path/123",  # Path not in query requirements mapping
            "pathParameters": {},
            "queryStringParameters": {},
        }
        context = MagicMock()

        result = handle_errors(event, context)
        assert result["errors"] == []

    @pytest.mark.parametrize("method", ["POST", "PUT", "PATCH"])
    def test_methods_without_body(self, method):
        """Test handle_errors for all methods that require a body"""
        event = {"httpMethod": method, "path": "/users"}
        if method in ["PUT", "PATCH"]:
            event["path"] = "/users/123"
            event["pathParameters"] = {"user_id": "123"}

        context = MagicMock()

        with pytest.raises(ValidationError) as exc:
            handle_errors(event, context)
        assert str(exc.value) == "Request body is required"

    @pytest.mark.parametrize("method", ["POST", "PUT", "PATCH"])
    def test_methods_with_body(self, method):
        """Test handle_errors for all methods with a valid body"""
        event = {
            "httpMethod": method,
            "path": "/users",
            "body": json.dumps({"name": "Test User"}),
        }
        if method in ["PUT", "PATCH"]:
            event["path"] = "/users/123"
            event["pathParameters"] = {"user_id": "123"}

        context = MagicMock()

        # This should not raise an exception
        result = handle_errors(event, context)
        assert result["errors"] == []

    def test_relationship_endpoint_exception(self):
        """Test handle_errors for relationship endpoints that don't require body"""
        event = {
            "httpMethod": "POST",
            "path": "/relationships/123/accept",
            "pathParameters": {"relationship_id": "123"}
            # Missing body is allowed for this endpoint
        }
        context = MagicMock()

        result = handle_errors(event, context)
        assert result["errors"] == []

    def test_short_path_with_body_check(self):
        """Test handle_errors for path too short for body exception check"""
        event = {
            "httpMethod": "POST",
            "path": "/relationships",  # Not enough parts for exception
            "pathParameters": {}
            # Missing body
        }
        context = MagicMock()

        with pytest.raises(ValidationError) as exc:
            handle_errors(event, context)
        assert str(exc.value) == "Request body is required"

    def test_different_relationship_action(self):
        """Test handle_errors for relationship action not in exceptions"""
        event = {
            "httpMethod": "POST",
            "path": "/relationships/123/cancel",  # 'cancel' not in exceptions
            "pathParameters": {"relationship_id": "123"}
            # Missing body
        }
        context = MagicMock()

        with pytest.raises(ValidationError) as exc:
            handle_errors(event, context)
        assert str(exc.value) == "Request body is required"

    def test_path_parts_length_mismatch(self):
        """Test handle_errors when path parts length doesn't match pattern"""
        event = {
            "httpMethod": "GET",
            "path": "/users",  # Only one part, pattern requires two
            "pathParameters": {},
        }
        context = MagicMock()

        result = handle_errors(event, context)
        assert result["errors"] == []

    def test_method_mismatch(self):
        """Test handle_errors when method doesn't match pattern"""
        event = {
            "httpMethod": "POST",  # Pattern requires GET
            "path": "/users/123",
            "pathParameters": {"user_id": "123"},
            "body": json.dumps({"name": "Test User"}),
        }
        context = MagicMock()

        result = handle_errors(event, context)
        assert result["errors"] == []

    def test_path_part_mismatch(self):
        """Test handle_errors when path part doesn't match pattern"""
        event = {
            "httpMethod": "GET",
            "path": "/accounts/123",  # Pattern requires 'users'
            "pathParameters": {"account_id": "123"},
        }
        context = MagicMock()

        result = handle_errors(event, context)
        assert result["errors"] == []

    def test_empty_errors_array(self):
        """Test that errors array is initialized if not present"""
        event = {}  # No errors array
        context = MagicMock()

        result = handle_errors(event, context)
        assert "errors" in result
        assert result["errors"] == []

    @pytest.mark.parametrize("test_case", generate_test_cases_for_path_params())
    def test_path_param_endpoints(self, test_case, mock_context):
        """Test all path parameter endpoints with valid data"""
        event = {
            "httpMethod": test_case["method"],
            "path": test_case["path"],
            "pathParameters": test_case["path_params"],
        }

        # Add a body for PUT, POST, PATCH methods to avoid body validation error
        if test_case["method"] in ["PUT", "POST", "PATCH"]:
            event["body"] = json.dumps({"data": "test"})

        # This should not raise an exception
        result = handle_errors(event, mock_context)
        assert result["errors"] == []

    @pytest.mark.parametrize("test_case", generate_test_cases_for_path_params())
    def test_path_param_endpoints_missing_param(self, test_case, mock_context):
        """Test all path parameter endpoints with missing parameters"""
        # Create event with empty path parameters
        event = {
            "httpMethod": test_case["method"],
            "path": test_case["path"],
            "pathParameters": {},  # Empty path parameters
        }

        # Add a body for PUT, POST, PATCH methods to avoid body validation error
        if test_case["method"] in ["PUT", "POST", "PATCH"]:
            event["body"] = json.dumps({"data": "test"})

        # This should raise a ValidationError
        with pytest.raises(ValidationError) as exc:
            handle_errors(event, mock_context)
        assert "Missing path parameter" in str(exc.value)

    @pytest.mark.parametrize("test_case", generate_test_cases_for_query_params())
    def test_query_param_endpoints(self, test_case, mock_context):
        """Test all query parameter endpoints with valid data"""
        event = {
            "httpMethod": test_case["method"],
            "path": test_case["path"],
            "pathParameters": test_case["path_params"],
            "queryStringParameters": test_case["query_params"],
        }

        # This should not add any errors
        result = handle_errors(event, mock_context)
        assert result["errors"] == []

    @pytest.mark.parametrize("test_case", generate_test_cases_for_query_params())
    def test_query_param_endpoints_missing_param(self, test_case, mock_context):
        """Test all query parameter endpoints with missing parameters"""
        event = {
            "httpMethod": test_case["method"],
            "path": test_case["path"],
            "pathParameters": test_case["path_params"],
            "queryStringParameters": {},  # Empty query parameters
        }

        # This should add errors for missing query parameters
        result = handle_errors(event, mock_context)
        for param in test_case["required_params"]:
            assert any(
                f"Missing query parameter: {param}" in error
                for error in result["errors"]
            )

    def test_no_matching_pattern_for_path_or_query(self):
        """Test handle_errors with a path that doesn't match any pattern"""
        event = {
            "httpMethod": "GET",
            "path": "/completely/random/path",
            "pathParameters": {"some_id": "123"},
            "queryStringParameters": {},
        }
        context = MagicMock()

        # This should not raise an exception
        result = handle_errors(event, context)
        assert result["errors"] == []

    def test_relationship_endpoint_exact_path(self):
        """Test the relationship endpoint exception precisely"""
        # Test both 'accept' and 'end' paths
        for action in ["accept", "end"]:
            event = {
                "httpMethod": "POST",
                "path": f"/relationships/123/{action}",
                "pathParameters": {"relationship_id": "123"}
                # Missing body is allowed for these endpoints
            }
            context = MagicMock()

            # This should not raise an exception
            result = handle_errors(event, context)
            assert result["errors"] == []

    def test_empty_body(self):
        """Test handle_errors with an empty body string"""
        event = {"httpMethod": "POST", "path": "/users", "body": ""}  # Empty string
        context = MagicMock()

        # This should raise an exception
        with pytest.raises(ValidationError) as exc:
            handle_errors(event, context)
        assert str(exc.value) == "Request body is required"

    def test_nonrelationship_path_with_depth(self):
        """Test a path with the right length but not a relationships path"""
        event = {
            "httpMethod": "POST",
            "path": "/users/123/activate",  # Same depth as relationships but different resource
            "pathParameters": {"user_id": "123"}
            # Missing body
        }
        context = MagicMock()

        # Should raise an exception
        with pytest.raises(ValidationError) as exc:
            handle_errors(event, context)
        assert str(exc.value) == "Request body is required"

    def test_handle_errors_path_mismatch(self):
        """Test handle_errors when path parts don't match pattern"""
        event = {
            "httpMethod": "GET",
            "path": "/some/path/with/different/length",
            "pathParameters": {},
        }
        result = handle_errors(event, MagicMock())
        assert result["errors"] == []

    def test_handle_errors_complex_path_matching(self):
        """Test handle_errors with more complex path matching"""
        # This tests the for loop and zip logic for path matching
        event = {
            "httpMethod": "GET",
            "path": "/users/123",
            "pathParameters": {"user_id": "123"},
        }
        result = handle_errors(event, MagicMock())
        assert result["errors"] == []

        # Test with mismatched path parts
        event = {
            "httpMethod": "GET",
            "path": "/userz/123",  # Slightly different path
            "pathParameters": {"user_id": "123"},
        }
        result = handle_errors(event, MagicMock())
        assert result["errors"] == []

    def test_handle_errors_query_params_edge_cases(self):
        """Test handle_errors with query parameter edge cases"""
        # Test query parameters with mismatched path parts
        event = {
            "httpMethod": "GET",
            "path": "/coaches/123/relationshipz",  # Slightly different
            "pathParameters": {"coach_id": "123"},
            "queryStringParameters": {},
        }
        result = handle_errors(event, MagicMock())
        assert result["errors"] == []

        # Test with null queryStringParameters
        event = {
            "httpMethod": "GET",
            "path": "/coaches/123/relationships",
            "pathParameters": {"coach_id": "123"},
            "queryStringParameters": None,
        }
        result = handle_errors(event, MagicMock())
        assert len(result["errors"]) > 0

    def test_handle_errors_relationship_endpoints(self):
        """Test handle_errors with relationship endpoints"""
        # Test the exception for relationship endpoints
        event = {
            "httpMethod": "POST",
            "path": "/relationships/123/accept",
            "pathParameters": {"relationship_id": "123"}
            # No body, but should be allowed for this endpoint
        }
        result = handle_errors(event, MagicMock())
        assert result["errors"] == []

        # Test with a different action that's not in the exceptions
        event = {
            "httpMethod": "POST",
            "path": "/relationships/123/cancel",  # 'cancel' not in exceptions
            "pathParameters": {"relationship_id": "123"}
            # No body
        }
        with pytest.raises(ValidationError):
            handle_errors(event, MagicMock())

        # Test with correct first part but not enough parts
        event = {
            "httpMethod": "POST",
            "path": "/relationships",
            "pathParameters": {}
            # No body
        }
        with pytest.raises(ValidationError):
            handle_errors(event, MagicMock())
