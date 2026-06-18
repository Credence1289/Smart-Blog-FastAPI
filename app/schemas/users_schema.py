from pydantic import BaseModel, EmailStr,field_validator
from typing import Optional

class UserIn(BaseModel):
    name : str
    email :EmailStr
    username : str
    password:str

    @field_validator("password")
    @classmethod
    def check_pass(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")

        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")

        return value
class UserOut(BaseModel):
    user_id: int
    name:str
    username:str
    email:EmailStr

class LoginReq(BaseModel):
    username : str
    password : str