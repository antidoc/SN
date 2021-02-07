from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from app.models.posts import PostCreate, PostPublic, PostUpdate
from app.models.users import UserInDB
from app.db.repositories.posts import PostsRepository
from app.db.repositories.events import EventsRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user


router = APIRouter()


@router.get("/", response_model=List[PostPublic], name="posts:get-all-posts")
async def get_all_posts(
        post_repo: PostsRepository = Depends(get_repository(PostsRepository)),
    ) -> List[PostPublic]:
    return await post_repo.get_all_posts()


@router.get("/{id}/", response_model=PostPublic, name="post:get-post-by-id")
async def get_post_by_id(
  id: int, posts_repo: PostsRepository = Depends(get_repository(PostsRepository))
) -> PostPublic:
    post = await posts_repo.get_post_by_id(id=id)
    if not post:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No post found with that id.")
    return post


@router.post("/", response_model=PostPublic, name="posts:create-post", status_code=HTTP_201_CREATED)
async def create_new_post(
        new_post: PostCreate = Body(..., embed=True),
        posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
        current_user: UserInDB = Depends(get_current_active_user)
) -> PostPublic:
    created_post = await posts_repo.create_post(new_post=new_post, author=current_user)

    await events_repo.create_post_event(user_id=current_user.id, post_id=created_post.id, event_type="post.create")
    return created_post

@router.put("/{id}/", response_model=PostUpdate, name="posts:update-post-by-id")
async def update_post_by_id(
        id: int = Path(..., ge=1, title="The ID of the post to update"),
        post_update: PostUpdate = Body(..., embed=True),
        post_repo: PostsRepository = Depends(get_repository(PostsRepository)),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
        current_user: UserInDB = Depends(get_current_active_user)
) -> PostPublic:

    updated_post = await post_repo.update_post(id=id, post_update=post_update, author=current_user.id)

    if not updated_post:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No post found with that id.")

    await events_repo.create_post_event(user_id=current_user.id, post_id=updated_post.id, event_type="post.update")
    return updated_post

@router.delete("/{id}/", response_model=int, name="posts:delete-post-by-id")
async def delete_post_by_id(
        id: int = Path(..., ge=1, title="The ID of the post to delete"),
        post_repo: PostsRepository = Depends(get_repository(PostsRepository)),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
        current_user: UserInDB = Depends(get_current_active_user)
) -> int:
    deleted_id = await post_repo.delete_post_by_id(id=id)

    if not deleted_id:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No post found with that id")

    await events_repo.create_user_event(user_id=current_user.id, event_type=f"post.delete(post_id={deleted_id})")
    return deleted_id

