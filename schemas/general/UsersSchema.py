from pydantic import BaseModel, EmailStr
import datetime


class BaseUsers(BaseModel):
    username: str
    email: EmailStr


class UserSignIn(BaseUsers):
    password: str


class UserSignOut(BaseUsers):
    created_at: datetime.datetime
    updated_at: datetime.datetime
