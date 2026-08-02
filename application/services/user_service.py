from collections.abc import Sequence
from uuid import UUID

from core.exceptions import ConflictError, NotFoundError
from domain.entities import User
from domain.repositories import UserRepository
from infrastructure.security.password_service import PasswordHasher


class UserService:
    """Owns user business rules; persistence remains behind a repository port."""

    def __init__(self, users: UserRepository, password_hasher: PasswordHasher):
        self._users = users
        self._password_hasher = password_hasher

    def create(self, email: str, full_name: str, password: str, *, is_superuser: bool = False) -> User:
        if self._users.get_by_email(email):
            raise ConflictError("An account with this email already exists")
        return self._users.create(
            email=email,
            full_name=full_name,
            password_hash=self._password_hasher.hash(password),
            is_superuser=is_superuser,
        )

    def get(self, user_id: UUID) -> User:
        user = self._users.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    def list(self, offset: int = 0, limit: int = 100) -> Sequence[User]:
        return self._users.list(offset, limit)

    def update(self, user_id: UUID, **values: object) -> User:
        if "email" in values and values["email"]:
            existing = self._users.get_by_email(str(values["email"]))
            if existing and existing.id != user_id:
                raise ConflictError("An account with this email already exists")
        if "password" in values:
            values["password_hash"] = self._password_hasher.hash(str(values.pop("password")))
        user = self._users.update(user_id, **values)
        if not user:
            raise NotFoundError("User not found")
        return user

    def delete(self, user_id: UUID) -> None:
        if not self._users.delete(user_id):
            raise NotFoundError("User not found")
