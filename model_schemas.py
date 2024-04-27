from pydantic import BaseModel, EmailStr
import datetime


class BaseReaders(BaseModel):
    username: str
    email: EmailStr
    disabled: bool = False


class UserSignIn(BaseReaders):
    password: str


class UserSignOut(BaseReaders):
    created_at: datetime.datetime
    updated_at: datetime.datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
