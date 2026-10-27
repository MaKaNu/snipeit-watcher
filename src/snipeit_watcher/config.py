from pydantic import EmailStr, Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Snipe-IT Config
    app_url: HttpUrl = HttpUrl("http://snipeit")

    # Mail Config
    mail_host: str | None = None
    mail_port: int = 25
    mail_from_addr: EmailStr | None = None
    mail_from_name: str = "Snipe-IT Watcher"

    # Snipe-IT Watcher Config
    snipeit_api_token: SecretStr | None = None
    disabled_users_id_whitelist: set[int] = Field(default_factory=set)
    watcher_interval: int = 5


settings = Settings()
