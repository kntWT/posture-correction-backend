from fastapi import APIRouter, Depends, Response
from schemas.user import User, UserCreateBasic, UserCreateEmail, UserCalibrate, UserBasicAuth, UserEmailAuth
from schemas.http_exception import BadRequestException, UnauthorizedException, ForbiddenException, error_responses
import cruds.user as crud
from typing import Union
from sqlalchemy.orm import Session
from guards.auth import login_auth, admin_auth
from configs.db import get_db
from configs.env import cookie_token_key
from helpers import jwt

user = APIRouter(prefix="/user", tags=["user"])


@user.get("/", response_model=list[User], responses=error_responses([UnauthorizedException, ForbiddenException]))
async def get_users(db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.get_users(db)


@user.get("/login", response_model=Union[User, None], responses=error_responses([UnauthorizedException]))
async def login(response: Response, _login: User = Depends(login_auth)):
    jwt = jwt.generate_token({"token": _login.token})
    response.set_cookie(key=cookie_token_key, value=jwt)
    return _login


@user.get("/login/basic", response_model=Union[User, None], responses=error_responses([UnauthorizedException]))
async def login_by_basic(name: str, password: str, response: Response, db: Session = Depends(get_db)):
    print(name, password)
    user: User = crud.get_user_by_basic(
        db, UserBasicAuth(name=name, password=password))
    if user is not None:
        jwt_token = jwt.generate_token({"token": user.token})
        print(jwt_token)
        response.set_cookie(key=cookie_token_key, value=jwt_token)
    return user


@user.get("/login/email", response_model=Union[User, None], responses=error_responses([UnauthorizedException]))
async def login_by_email(email: str, response: Response, db: Session = Depends(get_db)):
    user: User = crud.get_user_by_email(
        db, UserEmailAuth(email=email))
    if user is not None:
        jwt_token = jwt.generate_token({"token": user.token})
        response.set_cookie(key=cookie_token_key, value=jwt_token)
    return user


@user.get("/me/basic", response_model=bool)
async def is_exist_by_basic(name: str, password: str, db: Session = Depends(get_db)):
    return crud.get_user_by_basic(db, UserBasicAuth(name=name, password=password)) is not None


@user.get("/me/email", response_model=bool)
async def is_exist_by_email(email: str, db: Session = Depends(get_db)):
    return crud.get_user_by_email(db, UserEmailAuth(email=email)) is not None


@user.post("/create/basic", response_model=User, responses=error_responses([BadRequestException]))
async def create_user(user: UserCreateBasic, response: Response, db: Session = Depends(get_db)):
    user: User = crud.create_user_from_basic(db, user)
    jwt_token = jwt.generate_token({"token": user.token})
    response.set_cookie(key=cookie_token_key, value=jwt_token)
    return user


@user.post("/create/email", response_model=User, responses=error_responses([BadRequestException]))
async def create_user(user: UserCreateEmail, response: Response, db: Session = Depends(get_db)):
    user: User = crud.create_user_from_email(db, user)
    jwt_token = jwt.generate_token({"token": user.token})
    response.set_cookie(key=cookie_token_key, value=jwt_token)
    return user


@user.put("/calibrate", response_model=User, responses=error_responses([UnauthorizedException]))
async def calibrate_user(user: UserCalibrate, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.calibrate_user(db, user)


@user.put("/update", response_model=User, responses=error_responses([UnauthorizedException]))
async def update_user(user: User, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.update_user(db, user)
