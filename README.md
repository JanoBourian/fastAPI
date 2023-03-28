# fastAPI
The FastAPI course with AWS

## Information about Docker Container for PostgreSQL

From the Docker documentation we have the next code:

```cmd
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

```cmd
docker run -d --name postgresfastapi -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_USER=postgres -e PGDATA=/var/lib/postgresql/data/pgdata -p 5432:5432 -v C:\\Users\\super\\Documents\\database\\fastapidatabase:/var/lib/postgresql/data -d postgres
```

```cmd 
docker exec -it 481915eaf1ce psql -U postgres
```

## Packages

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

```cmd
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