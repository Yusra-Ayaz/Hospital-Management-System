from collections.abc import Sequence
from uuid import UUID
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from infrastructure.models import AppointmentModel, DoctorModel, MedicalRecordModel, PatientModel, UserModel


class BaseRepository:
    model = None
    def __init__(self, session: Session): self.session = session
    def get(self, item_id: UUID): return self.session.get(self.model, item_id)
    def list(self, offset: int = 0, limit: int = 20, search: str | None = None) -> Sequence:
        query = select(self.model)
        if search: query = self.search_query(query, search)
        return self.session.scalars(query.order_by(self.model.created_at.desc()).offset(offset).limit(limit)).all()
    def count(self) -> int: return self.session.scalar(select(func.count()).select_from(self.model)) or 0
    def create(self, **values):
        item = self.model(**values); self.session.add(item); self.session.commit(); self.session.refresh(item); return item
    def update(self, item_id: UUID, **values):
        item = self.get(item_id)
        if not item: return None
        for key, value in values.items(): setattr(item, key, value)
        self.session.commit(); self.session.refresh(item); return item
    def delete(self, item_id: UUID) -> bool:
        item = self.get(item_id)
        if not item: return False
        self.session.delete(item); self.session.commit(); return True
    def search_query(self, query, search: str): return query


class UserRepository(BaseRepository):
    model = UserModel
    def by_email(self, email: str): return self.session.scalar(select(UserModel).where(UserModel.email == email.lower()))


class PatientRepository(BaseRepository):
    model = PatientModel
    def search_query(self, query, term):
        like = f"%{term}%"; return query.where(or_(PatientModel.first_name.ilike(like), PatientModel.last_name.ilike(like), PatientModel.medical_record_number.ilike(like)))


class DoctorRepository(BaseRepository):
    model = DoctorModel
    def search_query(self, query, term):
        like = f"%{term}%"; return query.where(or_(DoctorModel.first_name.ilike(like), DoctorModel.last_name.ilike(like), DoctorModel.specialization.ilike(like)))


class AppointmentRepository(BaseRepository):
    model = AppointmentModel
    def list(self, offset=0, limit=20, search=None):
        query = select(AppointmentModel).options(selectinload(AppointmentModel.patient), selectinload(AppointmentModel.doctor)).order_by(AppointmentModel.scheduled_at.desc())
        return self.session.scalars(query.offset(offset).limit(limit)).all()
    def upcoming(self, limit=5):
        from datetime import datetime, timezone
        return self.session.scalars(select(AppointmentModel).options(selectinload(AppointmentModel.patient), selectinload(AppointmentModel.doctor)).where(AppointmentModel.scheduled_at >= datetime.now(timezone.utc)).order_by(AppointmentModel.scheduled_at).limit(limit)).all()

    def recent(self, limit=5):
        return self.session.scalars(select(AppointmentModel).options(selectinload(AppointmentModel.patient), selectinload(AppointmentModel.doctor)).order_by(AppointmentModel.created_at.desc()).limit(limit)).all()


class MedicalRecordRepository(BaseRepository):
    model = MedicalRecordModel
    def list(self, offset=0, limit=20, search=None):
        query = select(MedicalRecordModel).options(selectinload(MedicalRecordModel.patient), selectinload(MedicalRecordModel.doctor)).order_by(MedicalRecordModel.visit_date.desc())
        return self.session.scalars(query.offset(offset).limit(limit)).all()
