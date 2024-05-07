from fastapi import APIRouter, HTTPException, status
from fastapi.exceptions import ValidationException
from schemas.general import UsersSchema
import uuid
from managers import authentication
from asyncpg import UniqueViolationError
from models.user_cs import user_cs
import database_definition
from logger_config import logger

router = APIRouter(tags=["Register"])


@router.post("/register/", response_model=UsersSchema.UserSignOut, status_code=201)
async def create_user(user: UsersSchema.UserSignIn):
    try:
        user.password = authentication.get_password_hash(user.password)
        uuid_value = uuid.uuid4()
        data_to_insert = {"uuid": uuid_value, "is_active": False, **user.model_dump()}

        query = user_cs.insert().values(data_to_insert)
        await database_definition.database.execute(query)
        return await database_definition.database.fetch_one(
            user_cs.select().where(user_cs.c.uuid == uuid_value)
        )
    except ValidationException as e:
        logger.error(f"Something was wrong with the validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Some field has errors",
        )
    except UniqueViolationError as e:
        logger.error(f"Something was wrong with unique field: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that credentials already exists",
        )
    except Exception as e:
        logger.warning(f"Something was wrong with the server: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something was wrong",
        )
