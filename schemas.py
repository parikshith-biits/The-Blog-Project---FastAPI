from pydantic import BaseModel
from pydantic import EmailStr

class UserRegister(BaseModel):
    username:str
    email:EmailStr
    password:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class PostCreate(BaseModel):
    title:str
    content:str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int

    class Config:
        from_attributes = True

class RoleUpdate(BaseModel):
    role:str