from helpers.jwt import decode_token
from fastapi import Security, Depends
from fastapi.security import APIKeyCookie, HTTPBasic, HTTPBasicCredentials
from cruds.user import get_user_by_token
from schemas.user import User, UserGetByToken, UserBasicAuth
from schemas.http_exception import UnauthorizedException, TokenExpiredException, ForbiddenException, BadRequestException
from sqlalchemy.orm import Session
from configs.db import get_db
from configs.env import cookie_token_key

cookie_security = APIKeyCookie(name=cookie_token_key)


def login_auth(db: Session = Depends(get_db), token: str = Security(cookie_security)) -> User:
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


def admin_auth(db: Session = Depends(get_db), token: str = Security(cookie_security)) -> User:
    user = login_auth(db, token)
    if not user.is_admin:
        raise ForbiddenException("Forbidden")
    return user


basic_security = HTTPBasic()


def basic_auth(credentials: HTTPBasicCredentials = Security(basic_security)) -> dict[str, str]:
    return UserBasicAuth(name=credentials.username, password=credentials.password)
