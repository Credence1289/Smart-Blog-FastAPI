from pydantic import AnyUrl , Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: AnyUrl = Field(..., env="DATABASE_URL")
    SECRET_KEY:str = Field(..., env="SECRET_KEY")
    LOG_TOKEN:str = Field(..., env="LOG_TOKEN")
    ALGORITHM:str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRY_MIN:int = Field(30, env="ACCESS_TOKEN_EXPIRY_MIN")
    REFRESH_TOKEN_EXPIRY:int = Field(7, env="REFRESH_TOKEN_EXPIRY")

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    RESET_TOKEN_EXPIRE_MIN:str = Field(30, env="RESET_TOKEN_EXPIRE_MIN")

    MAIL_SERVER:str = Field("sandbox.smtp.mailtrap.io",env="MAIL_SERVER")
    MAIL_PORT:int = Field(2525,env="MAIL_PORT")
    MAIL_USERNAME:str = Field(...,env="MAIL_USERNAME")
    MAIL_PASSWORD:str = Field(...,env="MAIL_PASSWORD")
    MAIL_FROM:str = Field(..., env="MAIL_FROM")
    MAIL_USE_TLS:bool = Field(...,env="MAIL_USE_TLS")

    FRONTEND_URL:str = Field(...,env="FRONTEND_URL")
    
    REDIS_HOST:str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT:int = Field(6379, env="REDIS_PORT")
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()