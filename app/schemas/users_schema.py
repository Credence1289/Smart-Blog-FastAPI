from pydantic import BaseModel, EmailStr
from typing import Optional

class UserIn(BaseModel):
    name : str
    email :EmailStr
    username : str
    password:str

class UserOut(BaseModel):
    user_id: Optional[int] = None
    name:str
    username:str
    email:EmailStr

class LoginReq(BaseModel):
    username : str
    password : str