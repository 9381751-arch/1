from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase
    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_service_role_key: str = Field(alias="SUPABASE_SERVICE_ROLE_KEY")

    # Claude
    anthropic_api_key: str = Field(alias="ANTHROPIC_API_KEY")
    claude_model: str = Field(default="claude-sonnet-4-6", alias="CLAUDE_MODEL")

    # Telegram
    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
    tg_channel_requests_id: int = Field(alias="TG_CHANNEL_REQUESTS_ID")
    tg_group_sellers_id: int = Field(alias="TG_GROUP_SELLERS_ID")
    tg_manager_id: int = Field(alias="TG_MANAGER_ID")

    # OSRM
    osrm_base_url: str = Field(
        default="https://router.project-osrm.org", alias="OSRM_BASE_URL"
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


settings = Settings()  # type: ignore[call-arg]
