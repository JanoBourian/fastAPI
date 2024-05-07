from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.exceptions import ValidationException
from schemas.general import TokenSchema
from typing import Annotated
from managers import authentication
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from datetime import timedelta
from logger_config import logger
import env_configuration

router = APIRouter(tags=["Login"])


@router.post("/login/", status_code=201)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> TokenSchema.TokenResponse:
    try:
        user = await authentication.authenticate_user(
            form_data.username, form_data.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password or disabled user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(
            minutes=int(env_configuration.config.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
        )
        access_token = authentication.create_access_token(
            data={"sub": user.get("username")}, expires_delta=access_token_expires
        )
        return TokenSchema.TokenResponse(access_token=access_token, token_type="bearer")
    except HTTPException as e:
        logger.error(f"Something was wrong with authentication: {e}")
        raise e
    except ValidationException as e:
        logger.error(f"Something was wrong with the validation: {e}")
        raise HTTPException(422, "Some field has errors")
    except Exception as e:
        logger.warning(f"Something was wrong with the server: {e}")
        raise HTTPException(500, "Something was wrong")
