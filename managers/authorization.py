from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status
from typing import Annotated
import env_configuration
from jose import JWTError, jwt
import database_definition
from schemas.general import UsersSchema
from models import user_cs

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user(username: str):
    current_user = await database_definition.database.fetch_one(
        user_cs.select().where(user_cs.c.username == username)
    )
    return dict(current_user)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UsersSchema.BaseUsers:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            env_configuration.config.get("JWT_SECRET"),
            algorithms=[env_configuration.config.get("JWT_ALGORITHM")],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return UsersSchema.BaseUsers(**user)


async def get_current_active_user(
    current_user: Annotated[UsersSchema.BaseUsers, Depends(get_current_user)],
) -> UsersSchema.BaseUsers:
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_admin(
    current_user: Annotated[UsersSchema.BaseUsers, Depends(get_current_user)],
) -> UsersSchema.BaseUsers:
    if current_user.get("role").value != "admin":
        raise HTTPException(
            status_code=400, detail="You do not have permission for this action"
        )
    return current_user
