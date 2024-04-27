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
from typing import Optional, Annotated
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
import logging
import enum
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


class SizeEnum(enum.Enum):
    small = "s"
    medium = "m"
    large = "l"


class TypeBookEnum(enum.Enum):
    digital = "digital"
    physical = "physical"
    hybrid = "hybrid"


books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("uuid", sqlalchemy.Uuid, primary_key=True, unique=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("author", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("pages", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("size", sqlalchemy.Enum(SizeEnum), nullable=False),
    sqlalchemy.Column("type_book", sqlalchemy.Enum(TypeBookEnum), nullable=False),
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
    # sqlalchemy.Column("reader_uuid", sqlalchemy.ForeignKey("readers.uuid"), nullable=False, index=True),
)

readers = sqlalchemy.Table(
    "readers",
    metadata,
    sqlalchemy.Column("uuid", sqlalchemy.Uuid, primary_key=True, unique=True),
    sqlalchemy.Column("username", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("reader_role", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("disabled", sqlalchemy.Boolean, nullable=False, default=False),
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

readers_books = sqlalchemy.Table(
    "readers_books",
    metadata,
    sqlalchemy.Column("uuid", sqlalchemy.Uuid, primary_key=True, unique=True),
    sqlalchemy.Column("book_id", sqlalchemy.ForeignKey("books.uuid"), nullable=False),
    sqlalchemy.Column(
        "reader_id", sqlalchemy.ForeignKey("readers.uuid"), nullable=False
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
        readers.select().where(readers.c.username == username)
    )
    return dict(current_user)


async def authenticate_user(username: str, password: str):
    current_user = await data.fetch_one(
        readers.select().where(readers.c.username == username)
    )
    user_dict = dict(current_user)
    if not user_dict:
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


async def get_valid_admin(token: Annotated[str, Depends(oauth2_scheme)]):
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
    return user


async def get_current_valid_admin(
    current_user: Annotated[model_schemas.UserSignIn, Depends(get_valid_admin)],
):
    if current_user["reader_role"] != "admin":
        raise HTTPException(status_code=400, detail="User does not have access")
    return current_user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    return user


async def get_current_active_user(
    current_user: Annotated[model_schemas.UserSignIn, Depends(get_current_user)],
):
    if current_user["disabled"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/books/", tags=["books"], status_code=200)
async def get_all_books(
    user: Annotated[None, Depends(get_current_active_user)],
    _: Annotated[None, Depends(get_current_valid_admin)],
):
    query = books.select()
    return await data.fetch_all(query)


@app.post("/books/", tags=["books"], status_code=201)
async def create_book(request: Request):
    uuid_value = uuid.uuid4()
    body = await request.json()

    query = readers.select().where(readers.c.username == body.get("username"))
    reader = await data.fetch_one(query)
    dict_reader = dict(reader)

    data_to_insert = {
        "uuid": uuid_value,
        "title": body.get("title"),
        "author": body.get("author"),
        "pages": body.get("pages"),
        "reader_uuid": dict_reader.get("uuid"),
    }
    query = books.insert().values(**data_to_insert)
    await data.execute(query)
    return {"book": uuid_value}


# @app.get("/readers/", tags=["readers"])
# async def get_all_readers():
#     query = readers.select()
#     return await data.fetch_all(query)


# @app.post("/readers/", tags=["readers"])
# async def create_reader(request: Request):
#     uuid_value = uuid.uuid4()
#     body = await request.json()
#     body.update({"uuid": uuid_value})
#     query = readers.insert().values(**body)
#     await data.execute(query)
#     return {"reader": uuid_value}


@app.post("/read/", tags=["read"], status_code=201)
async def create_read_relation(request: Request):
    uuid_value = uuid.uuid4()
    body = await request.json()
    # Get reader
    book_query = books.select().where(books.c.title == body.get("title"))
    book_data = await data.fetch_one(book_query)
    book_dict = dict(book_data)
    # Get book
    reader_query = readers.select().where(readers.c.username == body.get("username"))
    reader_data = await data.fetch_one(reader_query)
    reader_dict = dict(reader_data)

    data_to_insert = {
        "uuid": uuid_value,
        "book_id": book_dict.get("uuid"),
        "reader_id": reader_dict.get("uuid"),
    }
    query = readers_books.insert().values(**data_to_insert)
    await data.execute(query)
    return {"reader_book": uuid_value}


@app.post("/register/", tags=["register"], response_model=model_schemas.UserSignOut, status_code=201)
async def create_user(user: model_schemas.UserSignIn):
    user.password = get_password_hash(user.password)
    uuid_value = uuid.uuid4()
    data_to_insert = {"uuid": uuid_value, **user.model_dump()}
    query = readers.insert().values(data_to_insert)
    await data.execute(query)
    return await data.fetch_one(readers.select().where(readers.c.uuid == uuid_value))


@app.post("/token/", tags=["token"], status_code=201)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request
) -> model_schemas.TokenResponse:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(config.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )
    access_token = create_access_token(
        data={"sub": user.get("username")}, expires_delta=access_token_expires
    )
    request.state.token = access_token
    return model_schemas.TokenResponse(access_token=access_token, token_type="bearer")
