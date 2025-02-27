class User:
    def __init__(self, user_id, email, name, role):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.role = role
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "role": self.role
        }