from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_VERSION: str = "1.0.0"

    # MongoDB
    MONGODB_URL: str = "mongodb://admin:admin@localhost:27017"
    MONGODB_DB_NAME: str = "claimflow_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Auth
    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # Storage
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    AWS_BUCKET_NAME: str = "claimflow-documents"
    S3_ENDPOINT_URL: str = "http://localhost:9000"

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"

    # AI
    GEMINI_API_KEY: str = ""

    # Email
    RESEND_API_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
