from passlib.context import CryptContext
import env_configuration
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import jwt
from schemas.general import TokenSchema
from models import user_cs
import database_definition

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str):
    current_user = await database_definition.database.fetch_one(
        user_cs.select().where(user_cs.c.username == username)
    )
    user_dict = dict(current_user)
    if not user_dict:
        return False
    if not user_dict.get("is_active"):
        return False
    if not verify_password(password, user_dict.get("password")):
        return False
    return user_dict


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        env_configuration.config.get("JWT_SECRET"),
        algorithm=env_configuration.config.get("JWT_ALGORITHM"),
    )
    return encoded_jwt


async def get_encode_token(username, password):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password or disabled user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(env_configuration.config.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )
    access_token = create_access_token(
        data={"sub": user.get("username")}, expires_delta=access_token_expires
    )
    return TokenSchema.TokenResponse(access_token=access_token, token_type="bearer")
