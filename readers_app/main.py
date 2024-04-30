from information import information
from passlib.context import CryptContext
import model_schemas
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
import uuid
import asyncio
import databases
import sqlalchemy
from dotenv import dotenv_values
from typing import Annotated, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
import logging
from jose import JWTError, jwt

logging.basicConfig(
    encoding="utf-8",
    format="%(levelname)7s:%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
    force=True,
)
logger = logging.getLogger()

config = {**dotenv_values(".env")}

DATABASE_URL = "%s://%s:%s@%s:%s/%s" % (
    config.get("DBDRIVER"),
    config.get("DBUSERNAME"),
    config.get("DBPASSWORD"),
    config.get("DBHOST"),
    config.get("DBPORT"),
    config.get("DBNAME"),
)

data = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("uuid", sqlalchemy.Uuid, primary_key=True, unique=True),
    sqlalchemy.Column("username", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("role", sqlalchemy.Enum(model_schemas.UserRolesEnum)),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean, nullable=False, default=False),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
    ),
    sqlalchemy.Column(
        "updated_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await data.connect()
    yield
    await data.disconnect()
    await asyncio.sleep(2)


information.update({"lifespan": lifespan})

app = FastAPI(**information)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str):
    current_user = await data.fetch_one(
        users.select().where(users.c.username == username)
    )
    return dict(current_user)


async def authenticate_user(username: str, password: str):
    current_user = await data.fetch_one(
        users.select().where(users.c.username == username)
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
        to_encode, config.get("JWT_SECRET"), algorithm=config.get("JWT_ALGORITHM")
    )
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> model_schemas.BaseUsers:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config.get("JWT_SECRET"), algorithms=[config.get("JWT_ALGORITHM")]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return model_schemas.BaseUsers(**user)


async def get_current_active_user(
    current_user: Annotated[model_schemas.BaseUsers, Depends(get_current_user)],
) -> model_schemas.BaseUsers:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_admin(
    current_user: Annotated[model_schemas.BaseUsers, Depends(get_current_user)],
) -> model_schemas.BaseUsers:
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=400, detail="You do not have permission for this action"
        )
    return current_user


@app.get(
    "/users/",
    tags=["users"],
    response_model=List[model_schemas.BaseUsers],
    status_code=200,
)
async def get_all_users(
    _: Annotated[List[model_schemas.BaseUsers], Depends(get_current_active_admin)]
):
    query = users.select()
    return await data.fetch_all(query)


@app.get("/me/", tags=["me"], response_model=model_schemas.BaseUsers, status_code=200)
async def get_current_user_information(
    user: Annotated[model_schemas.BaseUsers, Depends(get_current_active_user)]
):
    # print(f"USER in get_current_user_information: {user}")
    query = users.select().where(users.c.username == user.username)
    return await data.fetch_one(query)


@app.post(
    "/register/",
    tags=["register"],
    response_model=model_schemas.UserSignOut,
    status_code=201,
)
async def create_user(user: model_schemas.UserSignIn):
    user.password = get_password_hash(user.password)
    uuid_value = uuid.uuid4()
    data_to_insert = {"uuid": uuid_value, **user.model_dump()}
    query = users.insert().values(data_to_insert)
    await data.execute(query)
    return await data.fetch_one(users.select().where(users.c.uuid == uuid_value))


@app.post("/token/", tags=["token"], status_code=201)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> model_schemas.TokenResponse:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password or disabled user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(config.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )
    access_token = create_access_token(
        data={"sub": user.get("username")}, expires_delta=access_token_expires
    )
    return model_schemas.TokenResponse(access_token=access_token, token_type="bearer")
