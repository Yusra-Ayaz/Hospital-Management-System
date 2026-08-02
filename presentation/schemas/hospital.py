from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class ORM(BaseModel): model_config = ConfigDict(from_attributes=True)
class RegisterIn(BaseModel): email: EmailStr; full_name: str = Field(min_length=2, max_length=150); password: str = Field(min_length=8, max_length=128)
class LoginIn(BaseModel): email: EmailStr; password: str
class PatientIn(BaseModel):
    medical_record_number: str = Field(min_length=2, max_length=30); first_name: str = Field(min_length=1, max_length=80); last_name: str = Field(min_length=1, max_length=80); date_of_birth: date; gender: str = Field(min_length=1, max_length=20); phone: str = Field(min_length=3, max_length=30)
    email: EmailStr | None = None; address: str | None = None; blood_type: str | None = None; emergency_contact: str | None = None
class PatientOut(PatientIn, ORM): id: UUID
class DoctorIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=80); last_name: str = Field(min_length=1, max_length=80); specialization: str = Field(min_length=2, max_length=120); license_number: str = Field(min_length=2, max_length=60); phone: str = Field(min_length=3, max_length=30); email: EmailStr; room_number: str | None = Field(default=None, max_length=20)
class DoctorOut(DoctorIn, ORM): id: UUID
class AppointmentIn(BaseModel):
    patient_id: UUID; doctor_id: UUID; scheduled_at: datetime; reason: str = Field(min_length=3, max_length=2000); status: str = "scheduled"; notes: str | None = None
    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in {"scheduled", "confirmed", "completed", "cancelled"}:
            raise ValueError("Status must be scheduled, confirmed, completed, or cancelled")
        return value
class AppointmentOut(AppointmentIn, ORM): id: UUID
class MedicalRecordIn(BaseModel): patient_id: UUID; doctor_id: UUID | None = None; visit_date: date; diagnosis: str = Field(min_length=2, max_length=5000); treatment: str | None = None; prescription: str | None = None; allergies: str | None = None
class MedicalRecordOut(MedicalRecordIn, ORM): id: UUID
