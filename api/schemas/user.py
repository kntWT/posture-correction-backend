from datetime import datetime
from schemas.common import CamelCaseModel
from typing import Optional


class User(CamelCaseModel):
    id: int
    name: str = ""
    password: str = ""
    email: str | None
    icon_url: str | None = None
    token: str
    is_admin: bool = False
    standard_posture_id: int | None
    created_at: datetime
    updated_at: datetime

class UserWithoutToken(CamelCaseModel):
    id: int
    name: str
    password: str = ""
    email: str | None = None
    icon_url: str | None = None
    is_admin: bool = False
    standard_posture_id: int | None
    created_at: datetime
    updated_at: datetime


class UserUpdate(CamelCaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    icon_url: Optional[str] = None


class UserBasicAuth(CamelCaseModel):
    name: str
    password: str


class UserEmailAuth(CamelCaseModel):
    email: str


class UserCreateBasic(CamelCaseModel):
    name: str
    password: str
    is_admin: bool = False


class UserCreateEmail(CamelCaseModel):
    email: str
    name: str
    icon_url: str | None = None
    is_admin: bool = False


class UserGetByToken(CamelCaseModel):
    token: str


class UserCalibrate(CamelCaseModel):
    standard_posture_id: int


class UserId(CamelCaseModel):
    id: int
