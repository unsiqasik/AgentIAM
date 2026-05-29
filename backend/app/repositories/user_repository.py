from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import get_password_hash


class UserRepository:
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_id(self, db: Session, id: int) -> Optional[User]:
        return db.get(User, id)

    def create(self, db: Session, username: str, password: str, role: str) -> User:
        db_user = User(
            username=username,
            hashed_password=get_password_hash(password),
            role=UserRole(role),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


user_repository = UserRepository()
