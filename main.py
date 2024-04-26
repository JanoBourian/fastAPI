from information import information
from contextlib import asynccontextmanager
import uuid
import asyncio
import databases
import sqlalchemy
from dotenv import dotenv_values
from fastapi import FastAPI, Request
import enum

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
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False, unique=True),
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


@app.get("/books/", tags=["books"])
async def get_all_books():
    query = books.select()
    return await data.fetch_all(query)


@app.post("/books/", tags=["books"])
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


@app.get("/readers/", tags=["readers"])
async def get_all_readers():
    query = readers.select()
    return await data.fetch_all(query)


@app.post("/readers/", tags=["readers"])
async def create_reader(request: Request):
    uuid_value = uuid.uuid4()
    body = await request.json()
    body.update({"uuid": uuid_value})
    query = readers.insert().values(**body)
    await data.execute(query)
    return {"reader": uuid_value}


@app.post("/read/", tags=["read"])
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
