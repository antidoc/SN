from datetime import datetime

from app.db.repositories.base import BaseRepository
from app.models.users import UserInDB
from app.models.posts import PostInDB


INSERT_USER_EVENT_QUERY = """
    INSERT INTO events (user_id, event_type)
    VALUES (:user_id, :event_type);
"""

INSERT_POST_EVENT_QUERY = """
    INSERT INTO events (user_id, post_id, event_type)
    VALUES (:user_id, :post_id, :event_type);
"""

GET_USER_LAST_LOGIN_QUERY = """
    SELECT updated_at
    FROM events
    WHERE user_id = :user_id AND event_type = 'login'
    ORDER BY updated_at DESC
    LIMIT 1;
"""

GET_USER_LAST_ACTIVITY_QUERY = """
    SELECT updated_at
    FROM events
    WHERE user_id = :user_id
    ORDER BY updated_at DESC
    LIMIT 1;
"""

GET_ACTIVITY_BY_DATE = """
    SELECT
        DATE_TRUNC('day', created_at) AS aggregated_date, 
        count(*)
    FROM
      events
    WHERE updated_at BETWEEN :date_from AND :date_to
    AND event_type = :event_type
    GROUP BY aggregated_date
"""

class EventsRepository(BaseRepository):
    async def create_user_event(self, *, user_id: UserInDB, event_type: str):
        event_values = {"user_id": user_id, "event_type": event_type}
        created_event = await self.db.fetch_one(query=INSERT_USER_EVENT_QUERY, values=event_values)

    async def create_post_event(self, *, user_id: UserInDB, post_id: PostInDB, event_type: str):
        event_values = {"user_id": user_id, "post_id": post_id, "event_type": event_type}
        created_event = await self.db.fetch_one(query=INSERT_POST_EVENT_QUERY, values=event_values)

    async def get_user_activity(self, *, user_id: int):
        user_activity_values = {"user_id": user_id}
        user_last_login = await self.db.fetch_one(query=GET_USER_LAST_LOGIN_QUERY, values=user_activity_values)
        user_last_activity = await self.db.fetch_one(query=GET_USER_LAST_ACTIVITY_QUERY, values=user_activity_values)

        user_activity_json = {"last_login_time": user_last_login[0], "last_request_time": user_last_activity[0]}
        return user_activity_json

    async def get_aggregated_activity(self, *, date_from: str, date_to: str, event_type):
        aggregated_activity_values = {
            "date_from": datetime.fromisoformat(date_from),
            "date_to": datetime.fromisoformat(date_to),
            "event_type": event_type
        }
        aggregated_activity = await self.db.fetch_all(query=GET_ACTIVITY_BY_DATE, values=aggregated_activity_values)
        return aggregated_activity