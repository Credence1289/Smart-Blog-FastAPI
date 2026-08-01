from pydantic import BaseModel, ConfigDict, EmailStr,field_validator

class RefreshTokenIn(BaseModel):
    refresh_token: str

class AccessTokenOut(BaseModel):
    access_token: str
    token_type: str = "Bearer"

    model_config = ConfigDict(
        from_attributes = True
    )

class TokenOut(BaseModel):
    username:str
    access_token: str
    refresh_token:str
    token_type: str = "Bearer"

    model_config = ConfigDict(
        from_attributes = True
    )

class ForgotPasswordIn(BaseModel):
    email: EmailStr

class ResetPasswordIn(BaseModel):
    token:str
    new_password:str

    @field_validator("new_password")
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