import sqlalchemy
import enums_for_models
import database_definition

users_cs = sqlalchemy.Table(
    "users_cs",
    database_definition.metadata,
    sqlalchemy.Column("uuid", sqlalchemy.Uuid, primary_key=True, unique=True),
    sqlalchemy.Column("username", sqlalchemy.String(20), nullable=False, unique=True),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("role", sqlalchemy.Enum(enums_for_models.RoleType), nullable=False, server_default=enums_for_models.RoleType.user.name),
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

# Users data model