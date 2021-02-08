from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Path, Depends, HTTPException, Query
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY

from app.db.repositories.events import EventsRepository
from app.db.repositories.posts import PostsRepository
from app.db.repositories.users import UsersRepository
from app.models.users import UserInDB
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user

router = APIRouter()


@router.post("/{id}/like", response_model=str, name="events:like-post", status_code=HTTP_201_CREATED)
async def like_post(
        id: int = Path(..., ge=1, title="The ID of the post to like"),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
        posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
        current_user: UserInDB = Depends(get_current_active_user)
) -> Dict:
    post = await posts_repo.get_post_by_id(id=id)
    if not post:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No post found with that id.")

    like_id = await events_repo.create_post_event(user_id=current_user.id, post_id=id, event_type="post.like")
    return f"Post {id} was liked"


@router.post("/{id}/dislike", response_model=str, name="events:dislike-post", status_code=HTTP_201_CREATED)
async def dislike_post(
        id: int = Path(..., ge=1, title="The ID of the post to dislike"),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
        posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
        current_user: UserInDB = Depends(get_current_active_user)
):
    post = await posts_repo.get_post_by_id(id=id)
    if not post:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No post found with that id.")

    dislike_id = await events_repo.create_post_event(user_id=current_user.id, post_id=id, event_type="post.like")
    return f"Post {id} was disliked"

@router.get("/analitics/", name="events:get-aggregated-activity")
async def get_aggregated_activity(
        date_from: str,
        date_to: str,
        events_repo: EventsRepository = Depends(get_repository(EventsRepository))
        ) -> List:

    try:
        date_from = datetime.fromisoformat(date_from)
        date_to = datetime.fromisoformat(date_to)
    except:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Date range is incorrect"
        )

    aggregated_data = await events_repo.get_aggregated_activity(
        date_from=date_from,
        date_to=date_to,
        event_type="post.like"
    )
    return aggregated_data


@router.get("/{user_id}/", response_model=Dict, name="events:get-user-activity")
async def get_user_activity(
        user_id: int = Path(..., ge=1, title="User ID to get"),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    user = await users_repo.get_user_by_id(id=user_id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No user found with that id")

    user_activity = await events_repo.get_user_activity(user_id=user_id)
    return user_activity

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
