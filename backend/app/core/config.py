"""Env-driven application settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_prefix="ANIMAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    api_key: str = ""
    data_dir: Path = Field(default=Path("./data"))
    job_store: str = "memory"
    default_detection_provider: str = "stub-detection"
    default_pose_provider: str = "stub-pose"
    default_segmentation_provider: str = "stub-segmentation"
    default_inpainting_provider: str = "stub-inpainting"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def api_key_required(self) -> bool:
        return bool(self.api_key.strip())

    def ensure_data_dirs(self) -> None:
        for sub in ("images", "masks", "layers", "exports"):
            (self.data_dir / sub).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
