from pydantic import Field, MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False 
    )
    version: str = "0.0.2"
    env: str = Field(..., description="Ambiente da aplicação (dev, prod)")
    app_version: str = Field("0.0.1", description="Versão da aplicação")
    app_name: str = Field(default="PC Identidade", title="Nome da aplicação")
    memory_min: int = Field(default=64, title="Limite mínimo de memória disponível em MB")
    disk_usage_max: int = Field(default=80, title="Limite máximo de 80% de uso de disco")
    app_db_url_mongo: MongoDsn = Field(..., title="URI para o MongoDB")

settings = AppSettings()