from typing import Optional, Field
from app.models.core import CoreModel, IDModelMixin

class EventBase(CoreModel):
    user_id: Optional[int]
    post_id: Optional[int]
    event_type:Optional[str]

class EventCreate(CoreModel):
    pass

class EventUpdate(CoreModel):
    pass

class EventInDB(IDModelMixin, CoreModel):
    pass

class EventPublic(EventInDB):
    pass

class EventAggregated(CoreModel):
    date_from: str = Field()
    date_to: str = Field()
