from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: int
    name: str
    password: str
    email: str
    is_admin: bool
    neck_to_nose_standard: float | None
    created_at: datetime


class UserCreateBasic(BaseModel):
    name: str
    password: str
    is_admin: bool


class UserCreateEmail(BaseModel):
    email: str
    is_admin: bool


class UserCalibrate(BaseModel):
    id: int
    neck_to_nose_standard: Optional[float | None]


class UserId(BaseModel):
    id: int
