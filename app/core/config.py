from pydantic import AnyUrl , Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: AnyUrl = Field(..., env="DATABASE_URL")
    SECRET_KEY:str = Field(..., env="SECRET_KEY")
    LOG_TOKEN:str = Field(..., env="LOG_TOKEN")
    ALGORITHM:str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRY_MIN:int = Field(30, env="ACCESS_TOKEN_EXPIRY_MIN")
    REFRESH_TOKEN_EXPIRY:int = Field(7, env="REFRESH_TOKEN_EXPIRY")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()