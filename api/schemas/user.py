from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: int
    name: str
    password: str
    email: str
    neck_to_nose_standard: float | None
    created_at: datetime


class UserCreateBasic(BaseModel):
    name: str
    password: str


class UserCreateEmail(BaseModel):
    email: str


class UserCalibrate(BaseModel):
    id: int
    neck_to_nose_standard: Optional[float | None]


class UserId(BaseModel):
    id: int
