from application.services.hospital_service import AuthService

class Passwords:
    def hash(self, value): return "hash:" + value
    def verify(self, raw, hashed): return hashed == "hash:" + raw
class Users:
    def __init__(self): self.data = {}; self.created = []
    def by_email(self, email): return self.data.get(email)
    def count(self): return len(self.created)
    def create(self, **values):
        values["is_active"] = True
        self.created.append(values); self.data[values["email"]] = type("User",(),values)(); return self.data[values["email"]]
def test_first_registered_user_is_admin():
    users=Users(); user=AuthService(users, Passwords()).register("a@example.com","Ada","password123")
    assert user.role == "admin"
def test_authenticate_verifies_password():
    users=Users(); service=AuthService(users, Passwords()); service.register("a@example.com","Ada","password123")
    assert service.authenticate("a@example.com","password123").email == "a@example.com"
