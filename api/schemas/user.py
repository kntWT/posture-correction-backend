from datetime import datetime
from schemas.common import CamelCaseModel


class User(CamelCaseModel):
    id: int
    name: str = ""
    password: str = ""
    email: str | None
    token: str
    is_admin: bool = False
    standard_posture_id: int | None
    created_at: datetime

class UserWithoutToken(CamelCaseModel):
    id: int
    name: str = ""
    password: str = ""
    email: str | None
    is_admin: bool = False
    standard_posture_id: int | None
    created_at: datetime


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
    is_admin: bool = False


class UserGetByToken(CamelCaseModel):
    token: str


class UserCalibrate(CamelCaseModel):
    standard_posture_id: int


class UserId(CamelCaseModel):
    id: int
