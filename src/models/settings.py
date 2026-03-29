"""Settings-related Pydantic models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    """Application settings (subset persisted to YAML)."""

    last_output_dir: str = ""
    last_input_dir: str = ""
    zip_image_formats: list[str] = Field(default_factory=lambda: ["jpg", "jpeg", "png", "webp"])
    theme: str = "light"
    preserve_metadata: bool = True
    auto_increment: bool = True


class SettingsUpdate(BaseModel):
    """Partial settings update."""

    last_output_dir: str | None = None
    last_input_dir: str | None = None
    zip_image_formats: list[str] | None = None
    theme: str | None = None
    preserve_metadata: bool | None = None
    auto_increment: bool | None = None
