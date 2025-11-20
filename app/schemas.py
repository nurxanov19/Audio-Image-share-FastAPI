from pydantic import BaseModel
from fastapi_users import schemas
import uuid


class CreatePost(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    image_url: str

    class Config:
        from_attributes = True


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass