from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: Optional[str] = Field(default=None, description="Groq API Key")
    model_name: str = Field(default="llama-3.3-70b-versatile", description="Groq Model Identifier")
    app_env: str = Field(default="development", description="Application environment mode")
    request_timeout_seconds: int = Field(default=30, ge=5, le=120)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("groq_api_key")
    @classmethod
    def validate_groq_key(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_clean = v.strip()
            if not v_clean:
                return None
            return v_clean
        return None


settings = Settings()
