from pydantic import BaseModel, EmailStr,field_validator, ConfigDict

class UserIn(BaseModel):
    name : str
    email :EmailStr
    username : str
    password:str

    model_config = ConfigDict(
        extra="forbid",         #Reject unknown fields
        str_strip_whitespace=True  #remove spacing
    )

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

    model_config = ConfigDict(
        from_attributes = True #Read data from obj attributes
    )

class LoginReq(BaseModel):
    username : str
    password : str

    model_config = ConfigDict(
        extra="forbid"
    )