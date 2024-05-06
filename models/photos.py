import sqlalchemy
import database_definition

photos = sqlalchemy.Table(
    "photos",
    database_definition.metadata,
    sqlalchemy.Column("uuid", sqlalchemy.Uuid, primary_key=True, unique=True),
    sqlalchemy.Column("title", sqlalchemy.String(50), nullable=False, unique=True),
    sqlalchemy.Column("description", sqlalchemy.Text, nullable=False, unique=True),
    sqlalchemy.Column("url", sqlalchemy.String, nullable=False, unique=True),
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