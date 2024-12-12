import jwt
from datetime import datetime, timedelta
from typing import Optional
from jst import JST
from config.env import SECRET_KEY

ALGORITHM = "EdDSA"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # トークンの有効期限（分）


def generate_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(JST) + expires_delta
    else:
        expire = datetime.now(
            JST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
