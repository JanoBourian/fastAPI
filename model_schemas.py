from pydantic import BaseModel, EmailStr
import datetime


class BaseReaders(BaseModel):
    username: str
    email: EmailStr


class UserSignIn(BaseReaders):
    password: str


class UserSignOut(BaseReaders):
    created_at: datetime.datetime
    updated_at: datetime.datetime
