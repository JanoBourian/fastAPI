import sqlalchemy
import database_definition

user_cs_complaint = sqlalchemy.Table(
    "users_cs_complaint",
    database_definition.metadata,
    sqlalchemy.Column("uuid", sqlalchemy.Uuid, primary_key=True, unique=True),
    sqlalchemy.Column(
        "user_uuid", sqlalchemy.ForeignKey("users_cs.uuid"), nullable=False
    ),
    sqlalchemy.Column(
        "complaint_uuid", sqlalchemy.ForeignKey("complaints.uuid"), nullable=False
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
