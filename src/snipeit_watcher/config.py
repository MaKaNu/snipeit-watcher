from pydantic import EmailStr, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Snipe-IT Config
    app_url: HttpUrl = HttpUrl("http://snipeit")
    snipeit_api_token: SecretStr | None = None

    # Mail Config
    mail_host: str | None = None
    mail_port: int = 25
    mail_from_addr: EmailStr | None = None
    mail_from_name: str = "Snipe-IT Watcher"


settings = Settings()
