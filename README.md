# fastAPI
The FastAPI course with AWS

## Information about Docker Container for PostgreSQL

From the Docker documentation we have the next code:

```bash
docker run -d \
	--name postresfastapi \
	-e POSTGRES_PASSWORD=mysecretpassword \
	-e POSTGRES_USER=myusername \
	-e PGDATA=/var/lib/postgresql/data/pgdata \
	-p 5432:5432 \
	-v C:\\Users\\super\\Documents\\databases\\FastAPI:/var/lib/postgresql/data \
	-d postgres
```

We have other alternative

```bash
docker run -d --name fastapibd -e POSTGRES_PASSWORD=password -e POSTGRES_USER=username -e PGDATA=/var/lib/postgresql/data/pgdata -p 5433:5432 -v C:\\Users\\super\\Documents\\databases\\datainformation:/var/lib/postgresql/data -d postgres
```

```bash 
docker exec -it f9afd72f864b psql -U username
```

## Packages

* alembic
* sqlalchemy
* databases
* asyncpg
* psycopg2
* psycopg2-binary

## Books Store

* Books
* Readers
* Alembic migrations
* Different type of relationships

### For Books

The basic and first step, but in the future we will work with migrations (Alembic)

```python
import databases
import sqlalchemy

DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/store"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("author", sqlalchemy.String, nullable=False),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
```

### For start our application

Start the server 

```bash
uvicorn main:app --host 0.0.0.0 --port 80
uvicorn main:app --reload
```

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/books/")
async def get_all_books():
    query = books.select()
    return await database.fetch_all(query)

@app.post("/books/")
async def create_book(request:Request):
    data = await request.json()
    query = books.insert().values(**data)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}
```

## Alembic migration

We should change in *alembic.ini*  = sqlalchemy.url
We should change in *env.py* = target_metadata

```sh
alembic init migrations
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

## One to many

```python
books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("author", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("pages", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(
        "reader_id", sqlalchemy.ForeignKey("readers.id"), nullable=False, index=True
    ),
)

readers = sqlalchemy.Table(
    "readers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("last_name", sqlalchemy.String, nullable=False),
)
```

## Many-to-Many

```python
books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("author", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("pages", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(
        "reader_id", sqlalchemy.ForeignKey("readers.id"), nullable=False, index=True
    ),
)

readers = sqlalchemy.Table(
    "readers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("last_name", sqlalchemy.String, nullable=False),
)

readers_books = sqlalchemy.Table(
    "readers_books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column(
        "reader_id", sqlalchemy.ForeignKey("readers.id"), nullable=False, index=True
    ),
    sqlalchemy.Column(
        "book_id", sqlalchemy.ForeignKey("books.id"), nullable=False, index=True
    ),
)
```

## Python environment using decouple

```shell
pip install python-decouple
```

```python
from decouple import config

DATABASE_URL = f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@localhost:{config('DB_PORT')}/{config('DB_NAME')}"
```

## Containers

To run the backend container (with our docker-compose.yaml file)

```sh
docker build -t ivanova/fastapi:latest .
docker run -p 8080:80 --name ivanovafastapi dff825cddaca
```

Using the docker-compose file

```sh
docker-compose up --build
```