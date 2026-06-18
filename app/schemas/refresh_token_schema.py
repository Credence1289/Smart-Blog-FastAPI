from pydantic import BaseModel

class RefreshTokenReq(BaseModel):
    refresh_token: str