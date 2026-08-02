"""Server-rendered presentation routes for day-to-day hospital staff work."""
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from application.services.hospital_service import AppointmentService, AuthService, CrudService, MedicalRecordService
from core.config import get_settings
from core.dependencies import current_user
from database.session import get_db
from infrastructure.repositories.hospital_repositories import AppointmentRepository, DoctorRepository, MedicalRecordRepository, PatientRepository, UserRepository
from infrastructure.security.jwt_service import JWTService
from infrastructure.security.password_service import PasswordService
from presentation.schemas.hospital import AppointmentIn, DoctorIn, MedicalRecordIn, PatientIn

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="presentation/templates")


def redirect(path: str, message: str | None = None) -> RedirectResponse:
    suffix = f"?message={quote(message)}" if message else ""
    return RedirectResponse(path + suffix, status_code=303)


def resources(db: Session) -> dict[str, object]:
    return {"patients": PatientRepository(db), "doctors": DoctorRepository(db), "appointments": AppointmentRepository(db), "records": MedicalRecordRepository(db)}


def schemas() -> dict[str, type]:
    return {"patients": PatientIn, "doctors": DoctorIn, "appointments": AppointmentIn, "records": MedicalRecordIn}


@router.get("/")
def home(request: Request):
    """Public landing page; authenticated users can continue to their dashboard."""
    return templates.TemplateResponse(request, "home.html")


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post("/login")
def login(request: Request, email: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    user = AuthService(UserRepository(db), PasswordService()).authenticate(email, password)
    if not user:
        return templates.TemplateResponse(request, "login.html", {"error": "Invalid email or password"}, status_code=401)
    response = redirect("/dashboard", "Welcome back")
    response.set_cookie("access_token", JWTService().create_access_token(str(user.id)), httponly=True, samesite="lax", secure=get_settings().cookie_secure, max_age=60 * 60 * 8)
    return response


@router.post("/logout")
def logout():
    response = redirect("/login", "Signed out")
    response.delete_cookie("access_token")
    return response


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.post("/register")
def register(request: Request, full_name: str = Form(), email: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    try:
        AuthService(UserRepository(db), PasswordService()).register(email, full_name, password)
    except Exception as exc:
        return templates.TemplateResponse(request, "register.html", {"error": str(exc)}, status_code=400)
    return redirect("/login", "Account created. Please sign in.")


@router.get("/dashboard")
def dashboard(request: Request, user=Depends(current_user), db: Session = Depends(get_db)):
    appointments = AppointmentRepository(db)
    return templates.TemplateResponse(request, "dashboard.html", {"user": user, "counts": {"patients": PatientRepository(db).count(), "doctors": DoctorRepository(db).count(), "appointments": appointments.count(), "records": MedicalRecordRepository(db).count()}, "upcoming": appointments.upcoming(), "recent": appointments.recent()})


@router.get("/profile")
def profile(request: Request, user=Depends(current_user)):
    return templates.TemplateResponse(request, "profile.html", {"user": user})


@router.get("/{resource}")
def resource_list(resource: str, request: Request, edit: UUID | None = None, page: int = 1, user=Depends(current_user), db: Session = Depends(get_db)):
    repository = resources(db).get(resource)
    if not repository:
        return redirect("/dashboard")
    page_size = 10
    page = max(page, 1)
    total = repository.count()
    page_count = max(1, (total + page_size - 1) // page_size)
    page = min(page, page_count)
    editing = repository.get(edit) if edit else None
    return templates.TemplateResponse(request, "list.html", {"user": user, "resource": resource, "items": repository.list(offset=(page - 1) * page_size, limit=page_size), "patients": PatientRepository(db).list(limit=100), "doctors": DoctorRepository(db).list(limit=100), "editing": editing, "page": page, "page_count": page_count, "total": total})


def save(resource: str, values: dict, db: Session, item_id: UUID | None = None):
    repository = resources(db)[resource]
    if resource == "appointments":
        return AppointmentService(repository, PatientRepository(db), DoctorRepository(db)).update(item_id, values) if item_id else AppointmentService(repository, PatientRepository(db), DoctorRepository(db)).create(values)
    if resource == "records":
        service = MedicalRecordService(repository, PatientRepository(db), DoctorRepository(db))
        return service.update(item_id, values) if item_id else service.create(values)
    service = CrudService(repository)
    return service.update(item_id, values) if item_id else service.create(values)


async def form_values(resource: str, request: Request) -> dict:
    form = dict(await request.form())
    return schemas()[resource](**{key: value for key, value in form.items() if value != ""}).model_dump()


@router.post("/{resource}")
async def create_resource(resource: str, request: Request, user=Depends(current_user), db: Session = Depends(get_db)):
    if resource not in schemas():
        return redirect("/dashboard")
    try:
        save(resource, await form_values(resource, request), db)
    except Exception:
        return redirect(f"/{resource}", "Unable to save record. Check required fields and unique values.")
    return redirect(f"/{resource}", "Record saved")


@router.post("/{resource}/{item_id}")
async def update_resource(resource: str, item_id: UUID, request: Request, user=Depends(current_user), db: Session = Depends(get_db)):
    if resource not in schemas():
        return redirect("/dashboard")
    try:
        save(resource, await form_values(resource, request), db, item_id)
    except Exception:
        return redirect(f"/{resource}?edit={item_id}", "Unable to update record.")
    return redirect(f"/{resource}", "Record updated")


@router.post("/{resource}/{item_id}/delete")
def delete_resource(resource: str, item_id: UUID, user=Depends(current_user), db: Session = Depends(get_db)):
    repository = resources(db).get(resource)
    if not repository:
        return redirect("/dashboard")
    try:
        CrudService(repository).delete(item_id)
    except Exception:
        return redirect(f"/{resource}", "Unable to delete record.")
    return redirect(f"/{resource}", "Record deleted")
