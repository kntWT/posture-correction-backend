import jwt
from datetime import datetime, timedelta
from typing import Optional
from utils.jst import JST
from configs.env import secret_key

ALGORITHM = "EdDSA"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # トークンの有効期限（分）


def generate_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(JST) + expires_delta
    else:
        expire = datetime.now(
            JST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
