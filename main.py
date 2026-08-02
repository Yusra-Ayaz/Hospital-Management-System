import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from core.config import get_settings
from core.exceptions import ApplicationError, ConflictError, NotFoundError, ValidationError
from core.logging import configure_logging
from presentation.routers import hospital_api, web

configure_logging(); settings = get_settings(); logger = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name, version="1.0.0", description="Python-first Hospital Management System")
app.mount("/static", StaticFiles(directory=Path("presentation/static")), name="static")
@app.get("/manifest.webmanifest", include_in_schema=False)
def web_manifest(): return FileResponse("presentation/static/manifest.webmanifest", media_type="application/manifest+json")
@app.get("/service-worker.js", include_in_schema=False)
def service_worker(): return FileResponse("presentation/static/service-worker.js", media_type="application/javascript", headers={"Cache-Control": "no-cache"})
@app.exception_handler(ApplicationError)
async def app_error(_: Request, exc: ApplicationError):
    code = 404 if isinstance(exc, NotFoundError) else 409 if isinstance(exc, ConflictError) else 422 if isinstance(exc, ValidationError) else 400
    return JSONResponse(status_code=code, content={"detail":str(exc)})
@app.exception_handler(IntegrityError)
async def integrity_error(_: Request, exc: IntegrityError):
    logger.info("Database constraint violation: %s", exc.orig)
    return JSONResponse(status_code=409, content={"detail":"A record with one of these unique values already exists"})
@app.exception_handler(Exception)
async def unexpected(_: Request, exc: Exception):
    logger.exception("Unhandled error", exc_info=exc); return JSONResponse(status_code=500, content={"detail":"Internal server error"})
@app.get("/health", tags=["Health"])
def health(): return {"status":"ok", "environment":settings.environment}
app.include_router(web.router)
app.include_router(hospital_api.router, prefix="/api/v1")
