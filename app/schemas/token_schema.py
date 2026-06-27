from pydantic import BaseModel

class RefreshTokenIn(BaseModel):
    refresh_token: str

class AccessTokenOut(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class TokenOut(BaseModel):
    username:str
    access_token: str
    refresh_token:str
    token_type: str = "Bearer"