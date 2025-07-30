import base64
from typing import Optional
from helpers.jwt import decode_token
from fastapi import Security, Depends, status, Header
from fastapi.security import APIKeyCookie
from cruds.user import get_user_by_token
from schemas.user import User, UserGetByToken
from schemas.http_exception import UnauthorizedException, TokenExpiredException, ForbiddenException, BadRequestException
from sqlalchemy.orm import Session
from configs.db import get_db
from configs.env import cookie_token_key

security = APIKeyCookie(name=cookie_token_key)


def login_auth(db: Session = Depends(get_db), token: str = Security(security)) -> User:
    try:
        payload = decode_token(token)
        user = get_user_by_token(db, UserGetByToken(token=payload["token"]))
        if user is None:
            raise UnauthorizedException("Invalid token")
        return user
    except ValueError as e:
        if "expired" in str(e):
            raise TokenExpiredException("Token expired")
        else:
            raise UnauthorizedException("Invalid token")


def admin_auth(db: Session = Depends(get_db), token: str = Security(security)) -> User:
    user = login_auth(db, token)
    if not user.is_admin:
        raise ForbiddenException("Forbidden")
    return user


def basic_auth(authorization: Optional[str] = Header(None)) -> tuple[str, str]:
    if authorization is None or not authorization.startswith("Basic "):
        raise BadRequestException("Invalid authentication credentials")
    try:
        encoded_credentials = authorization.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        name, password = decoded_credentials.split(":", 1)
        return name, password
    except (ValueError, TypeError, IndexError):
        raise BadRequestException("Invalid authentication credentials")
