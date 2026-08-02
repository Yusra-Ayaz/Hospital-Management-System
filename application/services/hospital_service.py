from datetime import datetime
from uuid import UUID
from core.exceptions import ConflictError, NotFoundError, ValidationError


class CrudService:
    def __init__(self, repository): self.repository = repository
    def list(self, offset=0, limit=20, search=None): return self.repository.list(offset, limit, search)
    def get(self, item_id: UUID):
        item = self.repository.get(item_id)
        if not item: raise NotFoundError("Resource not found")
        return item
    def create(self, values: dict): return self.repository.create(**values)
    def update(self, item_id: UUID, values: dict):
        item = self.repository.update(item_id, **values)
        if not item: raise NotFoundError("Resource not found")
        return item
    def delete(self, item_id: UUID):
        if not self.repository.delete(item_id): raise NotFoundError("Resource not found")


class AppointmentService(CrudService):
    def __init__(self, repository, patients, doctors): super().__init__(repository); self.patients = patients; self.doctors = doctors
    def create(self, values):
        if not self.patients.get(values["patient_id"]): raise NotFoundError("Patient not found")
        if not self.doctors.get(values["doctor_id"]): raise NotFoundError("Doctor not found")
        if values["scheduled_at"] <= datetime.now(values["scheduled_at"].tzinfo): raise ValidationError("Appointment must be scheduled in the future")
        return super().create(values)

    def update(self, item_id: UUID, values: dict):
        if not self.patients.get(values["patient_id"]): raise NotFoundError("Patient not found")
        if not self.doctors.get(values["doctor_id"]): raise NotFoundError("Doctor not found")
        return super().update(item_id, values)


class MedicalRecordService(CrudService):
    """Ensures medical records always reference real clinical resources."""
    def __init__(self, repository, patients, doctors):
        super().__init__(repository); self.patients, self.doctors = patients, doctors

    def create(self, values: dict):
        self._validate_links(values)
        return super().create(values)

    def update(self, item_id: UUID, values: dict):
        self._validate_links(values)
        return super().update(item_id, values)

    def _validate_links(self, values: dict):
        if not self.patients.get(values["patient_id"]): raise NotFoundError("Patient not found")
        if values.get("doctor_id") and not self.doctors.get(values["doctor_id"]): raise NotFoundError("Doctor not found")


class AuthService:
    def __init__(self, users, passwords): self.users, self.passwords = users, passwords
    def register(self, email, full_name, password):
        if self.users.by_email(email): raise ConflictError("An account with this email already exists")
        return self.users.create(email=email.lower(), full_name=full_name, password_hash=self.passwords.hash(password), role="admin" if self.users.count() == 0 else "staff")
    def authenticate(self, email, password):
        user = self.users.by_email(email)
        if not user or not user.is_active or not self.passwords.verify(password, user.password_hash): return None
        return user
