from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # GitHub
    GITHUB_TOKEN: str | None = None

    # LLM
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str | None = None
    MODEL_NAME: str = "gemini-2.5-flash"
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "qwen/qwen3.8-27b"
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 1500

    # Repository source evidence
    SOURCE_MAX_FILES: int = Field(default=40, ge=1, le=200)
    SOURCE_MAX_FILE_BYTES: int = Field(default=16_000, ge=1, le=1_048_576)
    SOURCE_MAX_TOTAL_BYTES: int = Field(default=240_000, ge=1, le=5_242_880)
    SOURCE_MAX_CONCURRENCY: int = Field(default=5, ge=1, le=20)

    # API
    API_TITLE: str = "Atlas Backend"
    API_VERSION: str = "1.0.0"

    # Frontend Origins
    ALLOWED_ORIGINS: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"
        "http://localhost:8080,"
        "http://localhost:8081,"
        "http://127.0.0.1:3000,"
        "http://127.0.0.1:5173,"
        "http://127.0.0.1:8080,"
        "http://127.0.0.1:8081"
    )


    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        case_sensitive=True,
        extra="ignore",
    )

settings = Settings()
