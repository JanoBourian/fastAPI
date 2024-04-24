# FastAPI

## Working with Databases

```bash
docker run -d --name inavona -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_USER=myusername -e PGDATA=/var/lib/postgresql/data/pgdata -p 5434:5432 -v C:\\Users\\super\\Documents\\databases\\inavona:/var/lib/postgresql/data -d postgres
```

Packages: 
* alembic
* sqlalchemy
* databases
* python-dotenv
* asyncpg
* psycopg2
* psycopg2-binary

## Database configuration

The basic and first step, but in the future we will work with migrations (Alembic)

```python
import databases
import sqlalchemy
from dotenv import dotenv_values

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
    sqlalchemy.Column("uuid", sqlalchemy.Uuid, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("author", sqlalchemy.String, nullable=False),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
```