from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    name: str = ""
    password: str = ""
    email: str | None
    is_admin: bool = False
    standard_posture_id: int | None
    created_at: datetime


class UserBasicAuth(BaseModel):
    name: str
    password: str


class UserEmailAuth(BaseModel):
    email: str


class UserCreateBasic(BaseModel):
    name: str
    password: str
    is_admin: bool = False


class UserCreateEmail(BaseModel):
    email: str
    name: str
    is_admin: bool = False


class UserGetByToken(BaseModel):
    token: str


class UserCalibrate(BaseModel):
    standard_posture_id: int


class UserId(BaseModel):
    id: int
