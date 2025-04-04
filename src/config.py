from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str

    REDIS_HOST: str
    REDIS_PORT: int

    ADMIN_TELEGRAM_ID: int
    ADMIN_USERNAME: str

    MODEL: str
    DEVICE: str
    COMPUTE_TYPE: str
    DOWNLOAD_ROOT: str

    MODEL_URL: str
    EMAIL_MODEL: str
    PASSWORD_MODEL: str

    REQUEST_URL: str
    TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()
