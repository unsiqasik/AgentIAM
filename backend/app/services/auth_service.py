from sqlalchemy.orm import Session
from app.repositories.user_repository import user_repository
from app.core.security import verify_password, create_access_token


class AuthService:
    def authenticate(self, db: Session, username: str, password: str):
        user = user_repository.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def login(self, user):
        return {
            "access_token": create_access_token(user.id),
            "token_type": "bearer",
        }


auth_service = AuthService()
