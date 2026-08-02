from typing import Type
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from application.services.hospital_service import AppointmentService, AuthService, CrudService, MedicalRecordService
from core.config import get_settings
from core.dependencies import current_user
from database.session import get_db
from infrastructure.repositories.hospital_repositories import AppointmentRepository, DoctorRepository, MedicalRecordRepository, PatientRepository, UserRepository
from infrastructure.security.jwt_service import JWTService
from infrastructure.security.password_service import PasswordService
from presentation.schemas.hospital import *

router = APIRouter(tags=["Hospital API"])

@router.post("/auth/register", status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    try: user = AuthService(UserRepository(db), PasswordService()).register(payload.email, payload.full_name, payload.password)
    except IntegrityError: raise HTTPException(409, "Email already registered")
    return {"id": str(user.id), "email": user.email}

@router.post("/auth/login")
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = AuthService(UserRepository(db), PasswordService()).authenticate(payload.email, payload.password)
    if not user: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    token = JWTService().create_access_token(str(user.id))
    response.set_cookie("access_token", token, httponly=True, samesite="lax", secure=get_settings().cookie_secure, max_age=60 * 60 * 8)
    return {"message": "Signed in", "access_token": token, "token_type": "bearer", "user": {"name": user.full_name, "role": user.role}}

@router.post("/auth/logout", status_code=204)
def logout(response: Response): response.delete_cookie("access_token")

def crud_routes(path: str, repository_cls, schema_in: Type[BaseModel], schema_out: Type[BaseModel]):
    collection = APIRouter(prefix=path)
    def service(db): return CrudService(repository_cls(db))
    @collection.get("", response_model=list[schema_out])
    def list_items(offset: int = 0, limit: int = 20, search: str | None = None, _: object = Depends(current_user), db: Session = Depends(get_db)): return service(db).list(offset, min(limit, 100), search)
    @collection.post("", response_model=schema_out, status_code=201)
    def create_item(payload: schema_in, _: object = Depends(current_user), db: Session = Depends(get_db)): return service(db).create(payload.model_dump())
    @collection.get("/{item_id}", response_model=schema_out)
    def get_item(item_id: UUID, _: object = Depends(current_user), db: Session = Depends(get_db)): return service(db).get(item_id)
    @collection.put("/{item_id}", response_model=schema_out)
    def update_item(item_id: UUID, payload: schema_in, _: object = Depends(current_user), db: Session = Depends(get_db)): return service(db).update(item_id, payload.model_dump())
    @collection.delete("/{item_id}", status_code=204)
    def delete_item(item_id: UUID, _: object = Depends(current_user), db: Session = Depends(get_db)): service(db).delete(item_id)
    router.include_router(collection)

crud_routes("/patients", PatientRepository, PatientIn, PatientOut)
crud_routes("/doctors", DoctorRepository, DoctorIn, DoctorOut)
@router.get("/records", response_model=list[MedicalRecordOut])
def records(offset: int = 0, limit: int = 20, _: object = Depends(current_user), db: Session = Depends(get_db)):
    return MedicalRecordRepository(db).list(offset, min(limit, 100))

@router.post("/records", response_model=MedicalRecordOut, status_code=201)
def create_record(payload: MedicalRecordIn, _: object = Depends(current_user), db: Session = Depends(get_db)):
    return MedicalRecordService(MedicalRecordRepository(db), PatientRepository(db), DoctorRepository(db)).create(payload.model_dump())

@router.get("/records/{item_id}", response_model=MedicalRecordOut)
def get_record(item_id: UUID, _: object = Depends(current_user), db: Session = Depends(get_db)):
    return CrudService(MedicalRecordRepository(db)).get(item_id)

@router.put("/records/{item_id}", response_model=MedicalRecordOut)
def update_record(item_id: UUID, payload: MedicalRecordIn, _: object = Depends(current_user), db: Session = Depends(get_db)):
    return MedicalRecordService(MedicalRecordRepository(db), PatientRepository(db), DoctorRepository(db)).update(item_id, payload.model_dump())

@router.delete("/records/{item_id}", status_code=204)
def delete_record(item_id: UUID, _: object = Depends(current_user), db: Session = Depends(get_db)):
    CrudService(MedicalRecordRepository(db)).delete(item_id)

@router.get("/appointments", response_model=list[AppointmentOut])
def appointments(offset: int=0, limit: int=20, _: object=Depends(current_user), db: Session=Depends(get_db)): return AppointmentRepository(db).list(offset, min(limit,100))
@router.get("/appointments/{item_id}", response_model=AppointmentOut)
def get_appointment(item_id: UUID, _: object=Depends(current_user), db: Session=Depends(get_db)): return CrudService(AppointmentRepository(db)).get(item_id)
@router.post("/appointments", response_model=AppointmentOut, status_code=201)
def create_appointment(payload: AppointmentIn, _: object=Depends(current_user), db: Session=Depends(get_db)): return AppointmentService(AppointmentRepository(db), PatientRepository(db), DoctorRepository(db)).create(payload.model_dump())
@router.put("/appointments/{item_id}", response_model=AppointmentOut)
def update_appointment(item_id: UUID, payload: AppointmentIn, _: object=Depends(current_user), db: Session=Depends(get_db)): return AppointmentService(AppointmentRepository(db), PatientRepository(db), DoctorRepository(db)).update(item_id, payload.model_dump())
@router.delete("/appointments/{item_id}", status_code=204)
def delete_appointment(item_id: UUID, _: object=Depends(current_user), db: Session=Depends(get_db)): CrudService(AppointmentRepository(db)).delete(item_id)
