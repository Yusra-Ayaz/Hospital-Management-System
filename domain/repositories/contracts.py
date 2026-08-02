"""Repository ports. Infrastructure adapters implement these operations."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    @abstractmethod
    def get(self, item_id: UUID) -> T | None: ...

    @abstractmethod
    def list(self, offset: int = 0, limit: int = 20, search: str | None = None) -> list[T]: ...

    @abstractmethod
    def create(self, **values) -> T: ...

    @abstractmethod
    def update(self, item_id: UUID, **values) -> T | None: ...

    @abstractmethod
    def delete(self, item_id: UUID) -> bool: ...
