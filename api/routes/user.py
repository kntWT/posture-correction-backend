from fastapi import APIRouter, Depends
from schemas.user import User, UserCreateBasic, UserCreateEmail, UserCalibrate
from schemas.http_exception import BadRequestException, UnauthorizedException, ForbiddenException, error_responses
import cruds.user as crud
from typing import Union
from sqlalchemy.orm import Session
from guards.auth import login_auth, admin_auth
from configs.db import get_db

user = APIRouter(prefix="/user", tags=["user"])


@user.get("/", response_model=list[User], responses=error_responses([UnauthorizedException, ForbiddenException]))
async def get_users(db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.get_users(db)


@user.get("/me", response_model=Union[User, None], responses=error_responses([UnauthorizedException]))
async def get_me(_login: User = Depends(login_auth)):
    return _login


@user.post("/create/basic", response_model=User, responses=error_responses([BadRequestException]))
async def create_user(user: UserCreateBasic, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@user.post("/create/email", response_model=User, responses=error_responses([BadRequestException]))
async def create_user(user: UserCreateEmail, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@user.put("/calibrate", response_model=User, responses=error_responses([UnauthorizedException]))
async def calibrate_user(user: UserCalibrate, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.calibrate_user(db, user)


@user.put("/update", response_model=User, responses=error_responses([UnauthorizedException]))
async def update_user(user: User, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.update_user(db, user)
