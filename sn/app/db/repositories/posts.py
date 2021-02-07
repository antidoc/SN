from typing import List

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.db.repositories.base import BaseRepository
from app.models.posts import PostCreate, PostUpdate, PostInDB
from app.models.users import UserInDB

CREATE_POST_QUERY = """
    INSERT INTO posts (title, content, author)
    VALUES (:title, :content, :author)
    RETURNING id, title, content, author;
"""

GET_POST_BY_ID_QUERY = """
    SELECT id, title, content, author
    FROM posts
    WHERE id = :id;
"""

GET_ALL_POSTS_QUERY = """
    SELECT id, title, content, author
    FROM posts;
"""

UPDATE_POST_BY_ID_QUERY = """
    UPDATE posts
    SET title   = :title,
        content = :content,
        author  = :author
    WHERE id    = :id
    RETURNING id, title, content, author;
"""

DELETE_POST_BY_ID_QUERY = """
    DELETE FROM posts
    WHERE id = :id
    RETURNING id;
"""

class PostsRepository(BaseRepository):
    async def create_post(self, *, new_post: PostCreate, author: UserInDB) -> PostInDB:
        query_values = {**new_post.dict(), "author": author.id}
        post = await self.db.fetch_one(query=CREATE_POST_QUERY, values=query_values)

        return PostInDB(**post)

    async def get_post_by_id(self, *, id: int) -> PostInDB:
        post = await self.db.fetch_one(query=GET_POST_BY_ID_QUERY, values={"id": id})
        if not post:
            return None
        return PostInDB(**post)

    async def get_all_posts(self) -> List[PostInDB]:
        post_records = await self.db.fetch_all(query=GET_ALL_POSTS_QUERY)
        return [PostInDB(**l) for l in post_records]

    async def update_post(self, *, id: int, post_update: PostUpdate, author: UserInDB) -> PostInDB:
        post = await self.get_post_by_id(id=id)

        if not post:
            return None
        post_update_params = post.copy(update={**post_update.dict(exclude_unset=True), "author": author})

        if post_update_params.content is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid content. Cannot be None")

        try:
            updated_post = await self.db.fetch_one(query=UPDATE_POST_BY_ID_QUERY, values=post_update_params.dict())
            return PostInDB(**updated_post)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid update params")

    async def delete_post_by_id(self, *, id: int) -> int:
        post = await self.get_post_by_id(id=id)
        if not post:
            return None
        deleted_id = await self.db.execute(query=DELETE_POST_BY_ID_QUERY, values={"id": id})
        return deleted_id