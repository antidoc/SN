from typing import Optional
from pydantic import EmailStr

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from databases import Database

from app.db.repositories.base import BaseRepository
from app.models.users import UserCreate, UserUpdate, UserInDB
from app.services import auth_service

GET_USER_BY_EMAIL_QUERY = """
    SELECT id, username, email, password, salt, is_active, created_at, updated_at
    FROM users
    WHERE email = :email;
"""

GET_USER_BY_USERNAME_QUERY = """
    SELECT id, username, email, password, salt, is_active, created_at, updated_at
    FROM users
    WHERE username = :username;
"""

GET_USER_BY_ID_QUERY = """
    SELECT id, username, email, password, salt, is_active, created_at, updated_at
    FROM users
    WHERE id = :id;
"""

REGISTER_NEW_USER_QUERY = """
    INSERT INTO users(username, email, password, salt)
    VALUES (:username, :email, :password, :salt)
    RETURNING id, username, email, password, salt, is_active, created_at, updated_at
"""

class UsersRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_service = auth_service

    async def get_user_by_email(self, *, email: EmailStr) -> UserInDB:
        user_record = await self.db.fetch_one(query=GET_USER_BY_EMAIL_QUERY, values={"email": email})

        if not user_record:
            return None

        return UserInDB(**user_record)

    async def get_user_by_username(self, *, username: str) -> UserInDB:
        user_record = await self.db.fetch_one(query=GET_USER_BY_USERNAME_QUERY, values={"username": username})

        if not user_record:
            return None

        return UserInDB(**user_record)

    async def get_user_by_id(self, *, id: int) -> UserInDB:
        user_record = await self.db.fetch_one(query=GET_USER_BY_ID_QUERY, values={"id": id})

        if not user_record:
            return None

        return UserInDB(**user_record)

    async def register_new_user(self, *, new_user: UserCreate):
        if await self.get_user_by_email(email=new_user.email):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="That email is already taken. Login with this email or register with another one"
            )
        if await self.get_user_by_username(username=new_user.username):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="That username is already taken. Login with this username or register with another one"
            )

        user_password_update = self.auth_service.create_salt_and_hashed_password(plaintext_password=new_user.password)
        new_user_params = new_user.copy(update=user_password_update.dict())
        created_user = await self.db.fetch_one(query=REGISTER_NEW_USER_QUERY, values=new_user_params.dict())

        return UserInDB(**created_user)


    async def authenticate_user(self, *, email=EmailStr, password: str) -> Optional[UserInDB]:
        user = await self.get_user_by_email(email=email)
        if not user:
            return None
        if not self.auth_service.verify_password(password=password, salt=user.salt, hashed_pw=user.password):
            return None

        return user