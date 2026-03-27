"""Configuration loading and validation for LiteDocs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator


class GeoConfig(BaseModel):
    """Geographic SEO configuration."""

    enabled: bool = False
    default_region: str = ""


class SEOConfig(BaseModel):
    """SEO-related configuration."""

    auto_sitemap: bool = True
    auto_robots_txt: bool = True
    auto_llms_txt: bool = True
    og_image: str = ""
    structured_data: bool = True
    geo: GeoConfig = Field(default_factory=GeoConfig)


class AnalyticsConfig(BaseModel):
    """Analytics tracking configuration."""

    google_analytics: str = ""
    plausible: str = ""
    custom_head_scripts: list[str] = Field(default_factory=list)


class FooterLink(BaseModel):
    """A single footer link."""

    label: str
    href: str


class FooterConfig(BaseModel):
    """Footer configuration."""

    copyright: str = ""
    links: list[FooterLink] = Field(default_factory=list)


class ThemeConfig(BaseModel):
    """Theme configuration."""

    name: str = "default"
    primary_color: str = "#3b82f6"
    dark_mode: bool = True


class SiteSection(BaseModel):
    """Core site identity configuration."""

    title: str
    description: str = ""
    url: str = ""
    base_path: str = ""
    favicon: str = ""
    logo: str = ""


class LocalesSection(BaseModel):
    """Locale / i18n configuration."""

    default: str = "en"
    available: list[str] = Field(default_factory=lambda: ["en"])

    @model_validator(mode="after")
    def validate_default_in_available(self) -> "LocalesSection":
        if self.default not in self.available:
            raise ValueError(
                f"Default locale '{self.default}' must be in available locales: {self.available}"
            )
        return self


class SiteConfig(BaseModel):
    """Root configuration model loaded from config.json."""

    site: SiteSection
    locales: LocalesSection = Field(default_factory=LocalesSection)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    seo: SEOConfig = Field(default_factory=SEOConfig)
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    footer: FooterConfig = Field(default_factory=FooterConfig)
    flat_mode: bool = False


def load_config(docs_path: Path) -> SiteConfig:
    """Load and validate config.json from the documentation root directory.

    Args:
        docs_path: Path to the documentation root directory.

    Returns:
        Validated SiteConfig instance.

    Raises:
        FileNotFoundError: If config.json does not exist.
        ValueError: If config.json is invalid JSON or fails validation.
    """
    config_file = docs_path / "config.json"

    if not config_file.exists():
        raise FileNotFoundError(f"config.json not found in {docs_path}")

    try:
        raw: dict[str, Any] = json.loads(config_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {config_file}: {exc}") from exc

    return SiteConfig.model_validate(raw)
