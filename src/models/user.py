from typing import Dict, Literal, Any

class User:
    def __init__(self, user_id: str, email: str, name: str, role:Literal["athlete", "coach", "both"]):
        self.user_id: str = user_id
        self.email: str = email
        self.name: str = name
        self.role: Literal["athlete", "coach", "both"] = role
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "role": self.role
        }