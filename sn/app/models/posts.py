from typing import Optional

from app.models.core import IDModelMixin, CoreModel


class PostBase(CoreModel):
    title: Optional[str]
    content: Optional[str]

class PostCreate(PostBase):
    title: str
    content: str

class PostUpdate(PostBase):
    pass


class PostInDB(IDModelMixin, PostBase):
    title: str
    content: str
    author: int


class PostPublic(IDModelMixin, PostBase):
    pass
