from fastapi import APIRouter
from app.api.routes.posts import router as posts_router
from app.api.routes.users import router as users_router
from app.api.routes.events import router as events_router

router = APIRouter()
router.include_router(posts_router, prefix="/posts", tags=["posts"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(events_router, prefix="/activity", tags=["events"])