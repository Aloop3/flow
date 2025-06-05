import unittest
from src.models.user import User


class TestUserModel(unittest.TestCase):
    """
    Test suite for the User model
    """

    def test_user_initialization_athlete(self):
        """
        Test User model initialization with athlete role
        """
        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
        )

        self.assertEqual(user.user_id, "user123")
        self.assertEqual(user.email, "athlete@example.com")
        self.assertEqual(user.name, "Tyler Jones")
        self.assertEqual(user.role, "athlete")

    def test_user_initialization_coach(self):
        """
        Test User model initialization with coach role
        """
        user = User(
            user_id="user456", email="coach@example.com", name="John Doe", role="coach"
        )

        self.assertEqual(user.user_id, "user456")
        self.assertEqual(user.email, "coach@example.com")
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.role, "coach")

    def test_user_initialization_with_custom_exercises(self):
        """
        Test User model initialization with custom exercises
        """
        custom_exercises = [
            {"name": "Bulgarian Split Squat", "category": "BODYWEIGHT"},
            {"name": "Band Pull-Aparts", "category": "BODYWEIGHT"},
        ]

        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
            custom_exercises=custom_exercises,
        )

        self.assertEqual(user.user_id, "user123")
        self.assertEqual(user.email, "athlete@example.com")
        self.assertEqual(user.name, "Tyler Jones")
        self.assertEqual(user.role, "athlete")
        self.assertEqual(len(user.custom_exercises), 2)
        self.assertEqual(user.custom_exercises[0]["name"], "Bulgarian Split Squat")
        self.assertEqual(user.custom_exercises[1]["name"], "Band Pull-Aparts")

    def test_user_initialization_empty_custom_exercises(self):
        """
        Test User model initialization with empty custom exercises (default)
        """
        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
        )

        self.assertEqual(user.custom_exercises, [])

    def test_user_initialization_with_weight_preference_and_custom_exercises(self):
        """
        Test User model initialization with both weight preference and custom exercises
        """
        custom_exercises = [{"name": "Bulgarian Split Squat", "category": "BODYWEIGHT"}]

        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
            weight_unit_preference="kg",
            custom_exercises=custom_exercises,
        )

        self.assertEqual(user.weight_unit_preference, "kg")
        self.assertEqual(user.custom_exercises, custom_exercises)

    def test_user_to_dict(self):
        """
        Test User model to_dict method
        """
        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
        )

        user_dict = user.to_dict()

        self.assertEqual(user_dict["user_id"], "user123")
        self.assertEqual(user_dict["email"], "athlete@example.com")
        self.assertEqual(user_dict["name"], "Tyler Jones")
        self.assertEqual(user_dict["role"], "athlete")

    def test_user_to_dict_with_custom_exercises(self):
        """
        Test User model to_dict method includes custom exercises
        """
        custom_exercises = [{"name": "Bulgarian Split Squat", "category": "BODYWEIGHT"}]

        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
            custom_exercises=custom_exercises,
        )

        user_dict = user.to_dict()

        self.assertEqual(user_dict["user_id"], "user123")
        self.assertEqual(user_dict["email"], "athlete@example.com")
        self.assertEqual(user_dict["name"], "Tyler Jones")
        self.assertEqual(user_dict["role"], "athlete")
        self.assertEqual(user_dict["custom_exercises"], custom_exercises)
        self.assertEqual(len(user_dict["custom_exercises"]), 1)

    def test_user_to_dict_empty_custom_exercises(self):
        """
        Test User model to_dict method with empty custom exercises
        """
        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
        )

        user_dict = user.to_dict()

        self.assertEqual(user_dict["custom_exercises"], [])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
