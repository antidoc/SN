from typing import Optional

from pydantic import EmailStr, constr

from app.models.core import DateTimeModelMixin, IDModelMixin, CoreModel
from app.models.tokens import AccessToken


class UserBase(CoreModel):
    email: Optional[EmailStr]
    username: Optional[str]
    is_active: bool = True


class UserCreate(CoreModel):
    email: EmailStr
    password: constr(min_length=7, max_length=100)
    username: constr(min_length=3, regex="[a-zA-Z0-9_-]+$")


class UserUpdate(CoreModel):
    email: Optional[EmailStr]
    username: Optional[constr(min_length=3, regex="[a-zA-Z0-9_-]+$")]


class UserPasswordUpdate(CoreModel):
    password: constr(min_length=7, max_length=100)
    salt: str


class UserInDB(IDModelMixin, DateTimeModelMixin, UserBase):
    password: constr(min_length=7, max_length=100)
    salt: str


class UserPublic(IDModelMixin, DateTimeModelMixin, UserBase):
    access_token: Optional[AccessToken]

class UserID(IDModelMixin, UserBase):
    id: int