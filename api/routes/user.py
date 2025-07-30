import httpx
from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests
from schemas.user import User, UserCreateBasic, UserCreateEmail, UserCalibrate, UserBasicAuth, UserEmailAuth
from schemas.http_exception import BadRequestException, UnauthorizedException, ForbiddenException, TokenExpiredException, error_responses
import cruds.user as crud
from typing import Union
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from guards.auth import login_auth, admin_auth, basic_auth
from configs.db import get_db
from configs.env import cookie_token_key
from configs.oauth import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_AUTH_URL, GOOGLE_TOKEN_URL
from helpers import jwt

user = APIRouter(prefix="/user", tags=["user"])


@user.get("/", response_model=list[User], responses=error_responses([UnauthorizedException, ForbiddenException]))
async def get_users(db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.get_users(db)

@user.post("/auth/email", response_model=User, responses=error_responses([BadRequestException]))
async def login_or_create_by_email(user_create: UserCreateEmail, response: Response, db: Session = Depends(get_db)):
    exist_user = crud.get_user_by_email(db, UserEmailAuth(email=user_create.email))
    if exist_user is not None:
        return await login(response, exist_user)
    return await create_user_by_email(user_create, response, db)

@user.post("/auth/basic", response_model=User, responses=error_responses([BadRequestException]))
async def login_or_create_basic(user_create: UserCreateBasic, response: Response, db: Session = Depends(get_db)):
    exist_user = crud.get_user_by_basic(db, UserBasicAuth(name=user_create.name, password=user_create.password))
    if exist_user is not None:
        return await login(response, exist_user)
    return await create_user_basic(user_create, response, db)


@user.get("/login", response_model=Union[User, None], responses=error_responses([UnauthorizedException]))
async def login(response: Response, _login: User = Depends(login_auth)):
    jwt_token = jwt.generate_token({"token": _login.token})
    response.set_cookie(key=cookie_token_key, value=jwt_token, samesite="none", secure=True, httponly=True)
    return _login


@user.get("/login/basic", response_model=Union[User, None], responses=error_responses([UnauthorizedException]))
async def login_by_basic(response: Response, db: Session = Depends(get_db), basic_credential: UserBasicAuth = Depends(basic_auth)):
    user: User = crud.get_user_by_basic(
        db, basic_credential)
    if user is not None:
        jwt_token = jwt.generate_token({"token": user.token})
        response.set_cookie(key=cookie_token_key, value=jwt_token, samesite="none", secure=True, httponly=True)
    return user


@user.get("/login/email", response_model=Union[User, None], responses=error_responses([UnauthorizedException]))
async def login_by_email(email: str, response: Response, db: Session = Depends(get_db)):
    user: User = crud.get_user_by_email(
        db, UserEmailAuth(email=email))
    if user is not None:
        jwt_token = jwt.generate_token({"token": user.token})
        response.set_cookie(key=cookie_token_key, value=jwt_token, samesite="none", secure=True, httponly=True)
    return user


@user.get("/me/basic", response_model=bool)
async def is_exist_by_basic(name: str, password: str, db: Session = Depends(get_db)):
    return crud.get_user_by_basic(db, UserBasicAuth(name=name, password=password)) is not None


@user.get("/me/email", response_model=bool)
async def is_exist_by_email(email: str, db: Session = Depends(get_db)):
    return crud.get_user_by_email(db, UserEmailAuth(email=email)) is not None


@user.post("/create/basic", response_model=User, responses=error_responses([BadRequestException]))
async def create_user_basic(u: UserCreateBasic, response: Response, db: Session = Depends(get_db)):
    user: User | None = crud.create_user_from_basic(db, u)
    if user is None:
        raise BadRequestException("given user has already exists")
    jwt_token = jwt.generate_token({"token": user.token})
    response.set_cookie(key=cookie_token_key, value=jwt_token, samesite="none", secure=True, httponly=True)
    return user


@user.post("/create/email", response_model=User, responses=error_responses([BadRequestException]))
async def create_user_by_email(u: UserCreateEmail, response: Response, db: Session = Depends(get_db)):
    user: User | None = crud.create_user_from_email(db, u)
    if user is None:
        raise BadRequestException("given user has already exists")
    jwt_token = jwt.generate_token({"token": user.token})
    response.set_cookie(key=cookie_token_key, value=jwt_token, samesite="none", secure=True, httponly=True)
    return user

@user.get("/login/google", status_code=302)
async def login_google(redirect_to: str = "/"):
    params = urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email",
        "access_type": "offline",
        "prompt": "consent",
        "state": redirect_to,
    })
    google_auth_url = f"{GOOGLE_AUTH_URL}?{params}"
    return RedirectResponse(google_auth_url)

@user.get("/login/google/callback", status_code=302, responses=error_responses([BadRequestException, UnauthorizedException]))
async def google_callback(code: str, state: str, response: Response, db: Session = Depends(get_db)):
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        req = await client.post(GOOGLE_TOKEN_URL, data=data)
        req.raise_for_status()
        token_response = req.json()
    
    id_token_value = token_response.get("id_token")
    if id_token_value is None:
        raise BadRequestException("id_tokenが取得できませんでした")
    
    try:
        id_info = id_token.verify_oauth2_token(id_token_value, requests.Request(), GOOGLE_CLIENT_ID)
        
        name = id_info.get("name")
        email = id_info.get("email")
        if email is None:
            raise BadRequestException("Email is required for Google login")
        user = crud.get_user_by_email(db, UserEmailAuth(email=email))
        if user is None:
            user = crud.create_user_from_email(db, UserCreateEmail(email=email, name=name))
        if user is None:
            raise BadRequestException("User creation failed")
        jwt_token = jwt.generate_token({"token": user.token})
        response.set_cookie(key=cookie_token_key, value=jwt_token, samesite="none", secure=True, httponly=True)
        return RedirectResponse(url=state)
    
    except ValueError as e:
        raise BadRequestException(f"id_tokenの検証に失敗しました: {str(e)}") 
    
    except Exception as e:
        raise BadRequestException(f"エラーが発生しました: {str(e)}")

@user.post("/logout", response_model=bool, responses=error_responses([UnauthorizedException, TokenExpiredException]))
async def logout(response: Response, u: User = Depends(login_auth)):
    response.delete_cookie(key=cookie_token_key)
    return True


@user.put("/calibrate", response_model=User, responses=error_responses([UnauthorizedException]))
async def calibrate_user(user: UserCalibrate, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.calibrate_user(db, user, _login.token)


@user.put("/update", response_model=User, responses=error_responses([UnauthorizedException]))
async def update_user(user: User, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.update_user(db, user)
