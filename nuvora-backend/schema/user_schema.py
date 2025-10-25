from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    username: str
    user_passw: str

class UserResponse(BaseModel):
    id: int
    name: str
    username: str

class Config:
    from_attributes = True 