"""Configuration schema definitions."""

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class Config(BaseModel):
    """Validated runtime configuration loaded from environment variables."""

    model_config = ConfigDict(extra="forbid")

    api_url: AnyHttpUrl = Field(..., description="GraphQL API endpoint")
    api_key: str = Field(..., min_length=1, description="API authentication key")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Log level",
    )
