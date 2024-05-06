import sqlalchemy
import database_definition
import enums_for_models

complaints = sqlalchemy.Table(
    "complaints",
    database_definition.metadata,
    sqlalchemy.Column("uuid", sqlalchemy.Uuid, primary_key=True, unique=True),
    sqlalchemy.Column("title", sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column("description", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("amount", sqlalchemy.Float, nullable=False),
    sqlalchemy.Column(
        "photo_uuid", sqlalchemy.ForeignKey("photos.uuid"), nullable=False
    ),
    sqlalchemy.Column(
        "status",
        sqlalchemy.Enum(enums_for_models.State),
        nullable=False,
        server_default=enums_for_models.State.pending.name,
    ),
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
