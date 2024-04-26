from information import information
from contextlib import asynccontextmanager
import uuid
import asyncio
import databases
import sqlalchemy
from dotenv import dotenv_values
from fastapi import FastAPI, Request

config = {
    **dotenv_values('.env')
}

DATABASE_URL = '%s://%s:%s@%s:%s/%s'%(
    config.get("DBDRIVER"),
    config.get("DBUSERNAME"),
    config.get("DBPASSWORD"),
    config.get("DBHOST"),
    config.get("DBPORT"),
    config.get("DBNAME")
)

data = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("uuid", sqlalchemy.Uuid, primary_key=True, unique=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("author", sqlalchemy.String, nullable=False),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await data.connect()
    yield
    await data.disconnect()
    await asyncio.sleep(2)
    
information.update({
    "lifespan":lifespan
})

app = FastAPI(**information)

@app.get("/books/", tags=["books"])
async def get_all_books():
    query = books.select()
    return await data.fetch_all(query)

@app.post("/books/", tags=["books"])
async def create_book(request:Request):
    uuid_value = uuid.uuid4()
    body = await request.json()
    body.update({'uuid': uuid_value})
    query = books.insert().values(**body)
    await data.execute(query)
    return {"client": uuid_value}