from datetime import datetime, timedelta, timezone
import jwt
from core.config import get_settings


class JWTService:
    def create_access_token(self, subject: str) -> str:
        settings = get_settings()
        payload = {"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)}
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def decode(self, token: str) -> str | None:
        try:
            return jwt.decode(token, get_settings().jwt_secret_key, algorithms=[get_settings().jwt_algorithm]).get("sub")
        except jwt.PyJWTError:
            return None
