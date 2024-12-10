from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    name: str
    password: str
    email: str
    is_admin: bool
    standard_posture_id: int | None
    created_at: datetime


class UserCreateBasic(BaseModel):
    name: str
    password: str
    is_admin: bool


class UserCreateEmail(BaseModel):
    email: str
    is_admin: bool


class UserGetByToken(BaseModel):
    token: str


class UserCalibrate(BaseModel):
    id: int
    standard_posture_id: int


class UserId(BaseModel):
    id: int
