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
            role="athlete"
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
            user_id="user456",
            email="coach@example.com",
            name="John Doe",
            role="coach"
        )

        self.assertEqual(user.user_id, "user456")
        self.assertEqual(user.email, "coach@example.com")
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.role, "coach")
    
    def test_user_initialization_both(self):
        """
        Test User model initialization with both roles
        """
        user = User(
            user_id="user789",
            email="both@example.com",
            name="Jane Lee",
            role="both"
        )

        self.assertEqual(user.user_id, "user789")
        self.assertEqual(user.email, "both@example.com")
        self.assertEqual(user.name, "Jane Lee")
        self.assertEqual(user.role, "both")
    
    def test_user_to_dict(self):
        """
        Test User model to_dict method
        """
        user = User(
            user_id="user123",
            email="athlete@example.com",
            name="Tyler Jones",
            role="athlete"
        )

        user_dict = user.to_dict()

        self.assertEqual(user_dict["user_id"], "user123")
        self.assertEqual(user_dict["email"], "athlete@example.com")
        self.assertEqual(user_dict["name"], "Tyler Jones")
        self.assertEqual(user_dict["role"], "athlete")


if __name__ == "__main__": # pragma: no cover
    unittest.main()