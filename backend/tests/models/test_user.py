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

    def test_user_initialization_with_weight_unit_preference(self):
        """
        Test User model initialization with weight unit preference
        """
        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
            weight_unit_preference="kg",
        )

        self.assertEqual(user.user_id, "user123")
        self.assertEqual(user.email, "athlete@example.com")
        self.assertEqual(user.name, "Tyler Jones")
        self.assertEqual(user.role, "athlete")
        self.assertEqual(user.weight_unit_preference, "kg")

    def test_user_initialization_default_weight_unit_preference(self):
        """
        Test User model initialization with default weight unit preference
        """
        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
        )

        self.assertEqual(user.weight_unit_preference, "lb")

    def test_user_initialization_none_weight_unit_preference(self):
        """
        Test User model initialization with None weight unit preference defaults to lb
        """
        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
            weight_unit_preference=None,
        )

        self.assertEqual(user.weight_unit_preference, "lb")

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

    def test_user_to_dict_includes_weight_unit_preference(self):
        """
        Test User model to_dict method includes weight unit preference
        """
        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete",
            weight_unit_preference="kg",
        )

        result = user.to_dict()

        expected = {
            "user_id": "user123",
            "email": "athlete@example.com",
            "name": "Tyler Jones",
            "role": "athlete",
            "weight_unit_preference": "kg",
        }

        self.assertEqual(result, expected)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
