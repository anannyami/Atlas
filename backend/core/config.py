from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # GitHub
    GITHUB_TOKEN: str | None = None

    # LLM
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str | None = None
    MODEL_NAME: str = "gemini-flash-latest"
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 1500

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

print("CONFIG MODEL =", Settings().MODEL_NAME)
print("CONFIG TEMP =", Settings().TEMPERATURE)
print("CONFIG TOKENS =", Settings().MAX_TOKENS)
print("CONFIG KEY PREFIX =", Settings().GEMINI_API_KEY[:15])

settings = Settings()