"""Framework-independent domain entities used to document the hospital core."""
from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)
class Patient:
    id: UUID
    medical_record_number: str
    first_name: str
    last_name: str
    date_of_birth: date


@dataclass(frozen=True)
class Doctor:
    id: UUID
    first_name: str
    last_name: str
    specialization: str


@dataclass(frozen=True)
class Appointment:
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime
    status: str
