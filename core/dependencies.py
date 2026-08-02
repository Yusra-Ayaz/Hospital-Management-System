from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from database.session import get_db
from infrastructure.repositories.hospital_repositories import UserRepository
from infrastructure.security.jwt_service import JWTService


bearer_scheme = HTTPBearer(auto_error=False)


def current_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Accept the secure browser cookie and Bearer tokens for API clients."""
    token = request.cookies.get("access_token") or (credentials.credentials if credentials else None)
    user_id = JWTService().decode(token) if token else None
    user = UserRepository(db).get(user_id) if user_id else None
    if not user: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in")
    return user
