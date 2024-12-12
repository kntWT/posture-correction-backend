import secrets
from models.user import User
from schemas.user import UserCreateBasic, UserCreateEmail, UserGetByToken, UserCalibrate, UserId
from sqlalchemy.orm import Session


def get_users(db: Session) -> list[User]:
    return db.query(User).all()


def get_user_by_id(db: Session, user: UserId) -> User | None:
    return db.query(User).filter(User.id == user.id).one_or_none()


def get_user_by_token(db: Session, user: UserGetByToken) -> User | None:
    return db.query(User).filter(User.token == user.token).one_or_none()


def is_admin_by_token(db: Session, user: UserGetByToken) -> bool:
    u = db.query(User).filter(User.token == user.token).one_or_none()
    return None if u is None else u.is_admin


def create_user_from_basic(db: Session, user: UserCreateBasic) -> User:
    user.token = str(secrets.token_hex())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user_from_email(db: Session, user: UserCreateEmail) -> User:
    user.token = str(secrets.token_hex())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def calibrate_user(db: Session, user: UserCalibrate) -> User:
    user = db.query(User).filter(User.id == user.id).first()
    user.standard_posture_id = user.standard_posture_id
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User) -> User:
    u = get_user_by_token(db, UserGetByToken(token=user.token))
    if u is None:
        return None
    u = {**u.dict(), **user.dict()}
    db.commit()
    db.refresh(user)
    return user
