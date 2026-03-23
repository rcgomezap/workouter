from typing import Optional
from pydantic import BaseModel, Field, AnyHttpUrl, validator, HttpUrl


class ServerConfig(BaseModel):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    debug: bool = Field(default=False)


class DatabaseConfig(BaseModel):
    url: str = Field(default="sqlite+aiosqlite:///./data/workout_tracker.db")
    echo: bool = Field(default=False)


class AuthConfig(BaseModel):
    api_key: str


class LoggingConfig(BaseModel):
    level: str = Field(default="INFO")
    format: str = Field(default="json")
    file: Optional[str] = Field(default=None)


class ScheduledBackupConfig(BaseModel):
    enabled: bool = Field(default=False)
    frequency_hours: int = Field(default=24, ge=1)


class BackupConfig(BaseModel):
    enabled: bool = Field(default=True)
    directory: str = Field(default="./backups")
    scheduled: ScheduledBackupConfig = Field(default_factory=ScheduledBackupConfig)
    max_backups: int = Field(default=10, ge=1)


class PaginationConfig(BaseModel):
    default_page_size: int = Field(default=20, ge=1)
    max_page_size: int = Field(default=100, ge=1)


class Config(BaseModel):
    server: ServerConfig = Field(default_factory=ServerConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    auth: AuthConfig
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    backup: BackupConfig = Field(default_factory=BackupConfig)
    pagination: PaginationConfig = Field(default_factory=PaginationConfig)
