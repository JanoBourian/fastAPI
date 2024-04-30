from pydantic import BaseModel, EmailStr
import datetime
import enum


class SizeEnum(enum.Enum):
    small = "s"
    medium = "m"
    large = "l"


class TypeBookEnum(enum.Enum):
    digital = "digital"
    physical = "physical"
    hybrid = "hybrid"


class UserRolesEnum(enum.Enum):
    guest = "guest"
    user = "user"
    admin = "admin"


class ActiveUserEnum(enum.Enum):
    enabled = "enabled"
    disabled = "disabled"


class BaseReaders(BaseModel):
    username: str
    email: EmailStr
    disabled: bool = False


class BaseUsers(BaseModel):
    username: str
    email: EmailStr
    role: UserRolesEnum = UserRolesEnum.guest
    is_active: bool = False


class UserSignIn(BaseUsers):
    password: str


class UserSignOut(BaseUsers):
    created_at: datetime.datetime
    updated_at: datetime.datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
