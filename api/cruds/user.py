import secrets
from models.user import User as Model
from schemas.user import User, UserWithoutToken, UserCreateBasic, UserCreateEmail, UserGetByToken, UserCalibrate, UserId, UserBasicAuth, UserEmailAuth
from sqlalchemy.orm import Session


def get_users(db: Session) -> list[User]:
    users = db.query(Model).all()
    return [UserWithoutToken(**u.to_dict()) for u in users]


def get_user_by_id(db: Session, user: UserId) -> User | None:
    u = db.query(Model).filter(Model.id == user.id).one_or_none()
    return None if u is None else u


def get_user_by_basic(db: Session, user: UserBasicAuth) -> User | None:
    return db.query(Model).filter(Model.name == user.name).filter(
        Model.password == user.password).one_or_none()


def get_user_by_email(db: Session, user: UserEmailAuth) -> User | None:
    u = db.query(Model).filter(Model.email == user.email).one_or_none()
    return None if u is None else u


def get_user_by_token(db: Session, user: UserGetByToken) -> User | None:
    u = db.query(Model).filter(Model.token == user.token).one_or_none()
    return None if u is None else u


def is_admin_by_token(db: Session, user: UserGetByToken) -> bool:
    u = db.query(Model).filter(Model.token == user.token).one_or_none()
    return None if u is None else u.is_admin


def create_user_from_basic(db: Session, _user: UserCreateBasic) -> User | None:
    exist_user = get_user_by_basic(db, UserBasicAuth(name=_user.name, password=_user.password))
    if exist_user is not None:
        return None
    user = Model(**_user.model_dump())
    user.token = str(secrets.token_hex())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user_from_email(db: Session, _user: UserCreateEmail) -> User | None:
    exist_user = get_user_by_email(db, UserEmailAuth(email=_user.email))
    if exist_user is not None:
        return None
    user = Model(**_user.dict())
    user.token = str(secrets.token_hex())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def calibrate_user(db: Session, _user: UserCalibrate, token: str) -> User:
    user = get_user_by_token(db, UserGetByToken(token=token))
    user.standard_posture_id = _user.standard_posture_id
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User) -> User:
    u = get_user_by_token(db, UserGetByToken(token=user.token))
    if u is None:
        return None
    u = {**u, **user}
    db.commit()
    db.refresh(user)
    return user
