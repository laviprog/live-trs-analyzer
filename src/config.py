from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str

    REDIS_HOST: str
    REDIS_PORT: int

    MODEL: str
    DEVICE: str
    COMPUTE_TYPE: str
    DOWNLOAD_ROOT: str

    MODEL_URL: str
    EMAIL_MODEL: str
    PASSWORD_MODEL: str

    URL_REQUEST: str

    class Config:
        env_file = ".env"


settings = Settings()
