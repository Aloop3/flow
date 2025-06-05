from typing import Dict, Literal, Any, Optional, List


class User:
    def __init__(
        self,
        user_id: str,
        email: str,
        name: str,
        role: Optional[Literal["athlete", "coach"]] = None,
        weight_unit_preference: Optional[str] = "auto",
        custom_exercises: Optional[List[Dict[str, str]]] = None,
    ):
        self.user_id: str = user_id
        self.email: str = email
        self.name: str = name
        self.role: Optional[Literal["athlete", "coach"]] = role
        self.weight_unit_preference: Optional[str] = weight_unit_preference
        self.custom_exercises: Optional[List[Dict[str, str]]] = custom_exercises or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "weight_unit_preference": self.weight_unit_preference,
            "custom_exercises": self.custom_exercises,
        }
