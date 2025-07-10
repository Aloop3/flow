import unittest
from unittest.mock import MagicMock, patch
from src.middleware.middleware import ValidationError
from src.middleware.authorization_middleware import (
    validate_resource_ownership,
    _validate_user_access,
    _validate_athlete_access,
    _validate_creation_access,
    _is_active_coach,
    _get_athlete_from_block,
    _get_athlete_from_week,
    _get_athlete_from_day,
    _get_athlete_from_workout,
)


class TestAuthorizationMiddleware(unittest.TestCase):
    """
    Test suite for authorization middleware functions
    """

    def setUp(self):
        """Set up test fixtures with common mock data"""
        self.test_user_id = "test-user-123"
        self.test_athlete_id = "test-athlete-456"
        self.test_coach_id = "test-coach-789"
        self.test_block_id = "test-block-abc"
        self.test_week_id = "test-week-def"
        self.test_day_id = "test-day-ghi"
        self.test_workout_id = "test-workout-jkl"

        # Mock context
        self.mock_context = MagicMock()

    def _create_event(
        self, method="GET", resource="/test", path_params=None, user_id=None, body=None
    ):
        """Helper to create test events"""
        return {
            "httpMethod": method,
            "resource": resource,
            "pathParameters": path_params or {},
            "requestContext": {
                "authorizer": {"claims": {"sub": user_id or self.test_user_id}}
            },
            "body": body,
        }

    def test_validate_resource_ownership_missing_user_id(self):
        """Test authorization fails when user ID is missing from JWT claims"""
        event = {
            "httpMethod": "GET",
            "resource": "/users/{user_id}",
            "pathParameters": {"user_id": self.test_user_id},
            "requestContext": {},  # Missing authorizer claims
        }

        with self.assertRaises(ValidationError) as cm:
            validate_resource_ownership(event, self.mock_context)

        self.assertIn("Unauthorized - missing user ID", str(cm.exception))

    def test_validate_resource_ownership_skips_public_endpoints(self):
        """Test authorization is skipped for public endpoints"""
        event = self._create_event(resource="/exercises/types", path_params={})

        # Should not raise exception for public endpoint
        result = validate_resource_ownership(event, self.mock_context)
        self.assertEqual(result, event)

    def test_validate_user_access_own_data_success(self):
        """Test user can access their own data"""
        # Should not raise exception
        _validate_user_access(self.test_user_id, self.test_user_id)

    def test_validate_user_access_other_data_fails(self):
        """Test user cannot access other user's data"""
        other_user_id = "other-user-999"

        with self.assertRaises(ValidationError) as cm:
            _validate_user_access(self.test_user_id, other_user_id)

        self.assertIn("Forbidden - cannot access other user's data", str(cm.exception))

    def test_validate_athlete_access_own_data_success(self):
        """Test athlete can access their own data"""
        # Should not raise exception
        _validate_athlete_access(self.test_athlete_id, self.test_athlete_id)

    @patch("src.middleware.authorization_middleware._is_active_coach")
    def test_validate_athlete_access_coach_success(self, mock_is_active_coach):
        """Test coach can access athlete data with active relationship"""
        mock_is_active_coach.return_value = True

        # Should not raise exception
        _validate_athlete_access(self.test_coach_id, self.test_athlete_id)

        mock_is_active_coach.assert_called_once_with(
            self.test_coach_id, self.test_athlete_id
        )

    @patch("src.middleware.authorization_middleware._is_active_coach")
    def test_validate_athlete_access_non_coach_fails(self, mock_is_active_coach):
        """Test non-coach cannot access athlete data"""
        mock_is_active_coach.return_value = False

        with self.assertRaises(ValidationError) as cm:
            _validate_athlete_access(self.test_user_id, self.test_athlete_id)

        self.assertIn("Forbidden - no active coach relationship", str(cm.exception))

    @patch("src.services.relationship_service.RelationshipService")
    def test_is_active_coach_with_active_relationship(self, mock_relationship_service):
        """Test coach verification with active relationship"""
        # Mock relationship service
        mock_service_instance = mock_relationship_service.return_value
        mock_relationship = MagicMock()
        mock_relationship.status = "active"
        mock_service_instance.get_active_relationship.return_value = mock_relationship

        result = _is_active_coach(self.test_coach_id, self.test_athlete_id)

        self.assertTrue(result)
        mock_service_instance.get_active_relationship.assert_called_once_with(
            coach_id=self.test_coach_id, athlete_id=self.test_athlete_id
        )

    @patch("src.services.relationship_service.RelationshipService")
    def test_is_active_coach_with_no_relationship(self, mock_relationship_service):
        """Test coach verification with no relationship"""
        mock_service_instance = mock_relationship_service.return_value
        mock_service_instance.get_active_relationship.return_value = None

        result = _is_active_coach(self.test_coach_id, self.test_athlete_id)

        self.assertFalse(result)

    @patch("src.services.relationship_service.RelationshipService")
    def test_is_active_coach_with_inactive_relationship(
        self, mock_relationship_service
    ):
        """Test coach verification with inactive relationship"""
        mock_service_instance = mock_relationship_service.return_value
        mock_relationship = MagicMock()
        mock_relationship.status = "ended"
        mock_service_instance.get_active_relationship.return_value = mock_relationship

        result = _is_active_coach(self.test_coach_id, self.test_athlete_id)

        self.assertFalse(result)

    @patch("src.services.relationship_service.RelationshipService")
    def test_is_active_coach_with_exception(self, mock_relationship_service):
        """Test coach verification handles exceptions gracefully"""
        mock_service_instance = mock_relationship_service.return_value
        mock_service_instance.get_active_relationship.side_effect = Exception(
            "Database error"
        )

        result = _is_active_coach(self.test_coach_id, self.test_athlete_id)

        self.assertFalse(result)

    def test_validate_resource_ownership_user_id_endpoint(self):
        """Test authorization for endpoints with {user_id} parameter"""
        event = self._create_event(
            resource="/users/{user_id}",
            path_params={"user_id": self.test_user_id},
            user_id=self.test_user_id,
        )

        # Should not raise exception for user accessing own data
        result = validate_resource_ownership(event, self.mock_context)
        self.assertEqual(result, event)

    def test_validate_resource_ownership_user_id_endpoint_unauthorized(self):
        """Test authorization fails for {user_id} endpoint with wrong user"""
        event = self._create_event(
            resource="/users/{user_id}",
            path_params={"user_id": "other-user-999"},
            user_id=self.test_user_id,
        )

        with self.assertRaises(ValidationError) as cm:
            validate_resource_ownership(event, self.mock_context)

        self.assertIn("Forbidden - cannot access other user's data", str(cm.exception))

    @patch("src.middleware.authorization_middleware._validate_athlete_access")
    def test_validate_resource_ownership_athlete_id_endpoint(
        self, mock_validate_athlete
    ):
        """Test authorization for endpoints with {athlete_id} parameter"""
        event = self._create_event(
            resource="/athletes/{athlete_id}/workouts",
            path_params={"athlete_id": self.test_athlete_id},
            user_id=self.test_user_id,
        )

        result = validate_resource_ownership(event, self.mock_context)

        mock_validate_athlete.assert_called_once_with(
            self.test_user_id, self.test_athlete_id
        )
        self.assertEqual(result, event)

    @patch("src.middleware.authorization_middleware._get_athlete_from_week")
    @patch("src.middleware.authorization_middleware._validate_athlete_access")
    def test_validate_resource_ownership_week_id_endpoint(
        self, mock_validate_athlete, mock_get_athlete
    ):
        """Test authorization for endpoints with {week_id} parameter"""
        mock_get_athlete.return_value = self.test_athlete_id

        event = self._create_event(
            resource="/weeks/{week_id}",
            path_params={"week_id": self.test_week_id},
            user_id=self.test_user_id,
        )

        result = validate_resource_ownership(event, self.mock_context)

        mock_get_athlete.assert_called_once_with(self.test_week_id)
        mock_validate_athlete.assert_called_once_with(
            self.test_user_id, self.test_athlete_id
        )
        self.assertEqual(result, event)

    @patch("src.middleware.authorization_middleware._get_athlete_from_day")
    @patch("src.middleware.authorization_middleware._validate_athlete_access")
    def test_validate_resource_ownership_day_id_endpoint(
        self, mock_validate_athlete, mock_get_athlete
    ):
        """Test authorization for endpoints with {day_id} parameter"""
        mock_get_athlete.return_value = self.test_athlete_id

        event = self._create_event(
            resource="/days/{day_id}",
            path_params={"day_id": self.test_day_id},
            user_id=self.test_user_id,
        )

        result = validate_resource_ownership(event, self.mock_context)

        mock_get_athlete.assert_called_once_with(self.test_day_id)
        mock_validate_athlete.assert_called_once_with(
            self.test_user_id, self.test_athlete_id
        )
        self.assertEqual(result, event)

    @patch("src.middleware.authorization_middleware._get_athlete_from_workout")
    @patch("src.middleware.authorization_middleware._validate_athlete_access")
    def test_validate_resource_ownership_workout_id_endpoint(
        self, mock_validate_athlete, mock_get_athlete
    ):
        """Test authorization for endpoints with {workout_id} parameter"""
        mock_get_athlete.return_value = self.test_athlete_id

        event = self._create_event(
            resource="/workouts/{workout_id}",
            path_params={"workout_id": self.test_workout_id},
            user_id=self.test_user_id,
        )

        result = validate_resource_ownership(event, self.mock_context)

        mock_get_athlete.assert_called_once_with(self.test_workout_id)
        mock_validate_athlete.assert_called_once_with(
            self.test_user_id, self.test_athlete_id
        )
        self.assertEqual(result, event)

    @patch("src.middleware.authorization_middleware._get_athlete_from_block")
    @patch("src.middleware.authorization_middleware._validate_athlete_access")
    def test_validate_resource_ownership_block_id_endpoint(
        self, mock_validate_athlete, mock_get_athlete
    ):
        """Test authorization for endpoints with {block_id} parameter"""
        mock_get_athlete.return_value = self.test_athlete_id

        event = self._create_event(
            resource="/blocks/{block_id}",
            path_params={"block_id": self.test_block_id},
            user_id=self.test_user_id,
        )

        result = validate_resource_ownership(event, self.mock_context)

        mock_get_athlete.assert_called_once_with(self.test_block_id)
        mock_validate_athlete.assert_called_once_with(
            self.test_user_id, self.test_athlete_id
        )
        self.assertEqual(result, event)

    @patch("src.services.block_service.BlockService")
    def test_get_athlete_from_block_success(self, mock_block_service):
        """Test getting athlete ID from block ID"""
        mock_service_instance = mock_block_service.return_value
        mock_block = MagicMock()
        mock_block.athlete_id = self.test_athlete_id
        mock_service_instance.get_block.return_value = mock_block

        result = _get_athlete_from_block(self.test_block_id)

        self.assertEqual(result, self.test_athlete_id)
        mock_service_instance.get_block.assert_called_once_with(self.test_block_id)

    @patch("src.services.block_service.BlockService")
    def test_get_athlete_from_block_not_found(self, mock_block_service):
        """Test getting athlete ID from non-existent block"""
        mock_service_instance = mock_block_service.return_value
        mock_service_instance.get_block.return_value = None

        with self.assertRaises(ValidationError) as cm:
            _get_athlete_from_block(self.test_block_id)

        self.assertIn("Block not found", str(cm.exception))

    @patch("src.services.workout_service.WorkoutService")
    def test_get_athlete_from_workout_success(self, mock_workout_service):
        """Test getting athlete ID from workout ID"""
        mock_service_instance = mock_workout_service.return_value
        mock_workout = MagicMock()
        mock_workout.athlete_id = self.test_athlete_id
        mock_service_instance.get_workout.return_value = mock_workout

        result = _get_athlete_from_workout(self.test_workout_id)

        self.assertEqual(result, self.test_athlete_id)
        mock_service_instance.get_workout.assert_called_once_with(self.test_workout_id)

    @patch("src.services.workout_service.WorkoutService")
    def test_get_athlete_from_workout_not_found(self, mock_workout_service):
        """Test getting athlete ID from non-existent workout"""
        mock_service_instance = mock_workout_service.return_value
        mock_service_instance.get_workout.return_value = None

        with self.assertRaises(ValidationError) as cm:
            _get_athlete_from_workout(self.test_workout_id)

        self.assertIn("Workout not found", str(cm.exception))

    @patch("src.services.week_service.WeekService")
    @patch("src.middleware.authorization_middleware._get_athlete_from_block")
    def test_get_athlete_from_week_success(
        self, mock_get_athlete_from_block, mock_week_service
    ):
        """Test getting athlete ID from week ID via block"""
        mock_service_instance = mock_week_service.return_value
        mock_week = MagicMock()
        mock_week.block_id = self.test_block_id
        mock_service_instance.get_week.return_value = mock_week
        mock_get_athlete_from_block.return_value = self.test_athlete_id

        result = _get_athlete_from_week(self.test_week_id)

        self.assertEqual(result, self.test_athlete_id)
        mock_service_instance.get_week.assert_called_once_with(self.test_week_id)
        mock_get_athlete_from_block.assert_called_once_with(self.test_block_id)

    @patch("src.services.week_service.WeekService")
    def test_get_athlete_from_week_not_found(self, mock_week_service):
        """Test getting athlete ID from non-existent week"""
        mock_service_instance = mock_week_service.return_value
        mock_service_instance.get_week.return_value = None

        with self.assertRaises(ValidationError) as cm:
            _get_athlete_from_week(self.test_week_id)

        self.assertIn("Week not found", str(cm.exception))

    @patch("src.services.day_service.DayService")
    @patch("src.middleware.authorization_middleware._get_athlete_from_week")
    def test_get_athlete_from_day_success(
        self, mock_get_athlete_from_week, mock_day_service
    ):
        """Test getting athlete ID from day ID via week and block"""
        mock_service_instance = mock_day_service.return_value
        mock_day = MagicMock()
        mock_day.week_id = self.test_week_id
        mock_service_instance.get_day.return_value = mock_day
        mock_get_athlete_from_week.return_value = self.test_athlete_id

        result = _get_athlete_from_day(self.test_day_id)

        self.assertEqual(result, self.test_athlete_id)
        mock_service_instance.get_day.assert_called_once_with(self.test_day_id)
        mock_get_athlete_from_week.assert_called_once_with(self.test_week_id)

    @patch("src.services.day_service.DayService")
    def test_get_athlete_from_day_not_found(self, mock_day_service):
        """Test getting athlete ID from non-existent day"""
        mock_service_instance = mock_day_service.return_value
        mock_service_instance.get_day.return_value = None

        with self.assertRaises(ValidationError) as cm:
            _get_athlete_from_day(self.test_day_id)

        self.assertIn("Day not found", str(cm.exception))

    @patch("src.middleware.authorization_middleware._get_athlete_from_day")
    @patch("src.middleware.authorization_middleware._validate_athlete_access")
    def test_validate_creation_access_day_workout(
        self, mock_validate_athlete, mock_get_athlete
    ):
        """Test validation for creating day workout"""
        mock_get_athlete.return_value = self.test_athlete_id

        event = self._create_event(
            method="POST",
            resource="/days/{day_id}/workout",
            path_params={"day_id": self.test_day_id},
            user_id=self.test_user_id,
            body='{"exercises": []}',
        )

        _validate_creation_access(self.test_user_id, event, "/days/{day_id}/workout")

        mock_get_athlete.assert_called_once_with(self.test_day_id)
        mock_validate_athlete.assert_called_once_with(
            self.test_user_id, self.test_athlete_id
        )

    def test_validate_creation_access_athlete_id_in_body(self):
        """Test validation for creation with athlete_id in request body"""
        event = self._create_event(
            method="POST",
            resource="/blocks",
            body=f'{{"athlete_id": "{self.test_athlete_id}", "name": "Test Block"}}',
        )

        with patch(
            "src.middleware.authorization_middleware._validate_athlete_access"
        ) as mock_validate:
            _validate_creation_access(self.test_user_id, event, "/blocks")
            mock_validate.assert_called_once_with(
                self.test_user_id, self.test_athlete_id
            )

    def test_validate_creation_access_invalid_json(self):
        """Test validation handles invalid JSON gracefully"""
        event = self._create_event(
            method="POST", resource="/blocks", body="{invalid json}"
        )

        # Should not raise exception for invalid JSON (handled by other middleware)
        _validate_creation_access(self.test_user_id, event, "/blocks")

    def test_validate_resource_ownership_post_request_with_validation(self):
        """Test POST request triggers creation access validation"""
        event = self._create_event(
            method="POST",
            resource="/blocks",
            user_id=self.test_user_id,
            body=f'{{"athlete_id": "{self.test_athlete_id}", "name": "Test"}}',
        )

        with patch(
            "src.middleware.authorization_middleware._validate_creation_access"
        ) as mock_validate:
            result = validate_resource_ownership(event, self.mock_context)
            mock_validate.assert_called_once_with(self.test_user_id, event, "/blocks")
            self.assertEqual(result, event)

    def test_validate_resource_ownership_handles_exceptions(self):
        """Test authorization middleware handles unexpected exceptions"""
        event = self._create_event(
            resource="/users/{user_id}", path_params={"user_id": self.test_user_id}
        )

        with patch(
            "src.middleware.authorization_middleware._validate_user_access",
            side_effect=Exception("Unexpected error"),
        ):
            with self.assertRaises(ValidationError) as cm:
                validate_resource_ownership(event, self.mock_context)

            self.assertIn("Access validation failed", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
