from abc import ABC, abstractmethod

from passlib.context import CryptContext


class PasswordHasher(ABC):
    """Password hashing port; alternate algorithms can substitute this adapter."""

    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, password: str, password_hash: str) -> bool: ...


class BcryptPasswordHasher(PasswordHasher):
    _context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self._context.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        return self._context.verify(password, password_hash)


# Concrete adapter used by dependency injection in the web/API layer.
PasswordService = BcryptPasswordHasher
