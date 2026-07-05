from pydantic import BaseModel, ConfigDict

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