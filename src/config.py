import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    db_host: str
    db_port: int = 5432
    db_user: str
    db_name: str
    db_password: str

    model_config = SettingsConfigDict(extra='ignore', env_file=".env")

db_settings = PostgresSettings()

def get_postgres_uri():
    host = db_settings.db_host
    port = db_settings.db_port
    password = db_settings.db_password
    user, db_name = db_settings.db_user, db_settings.db_name
    return f'postgresql://{user}:{password}@{host}:{port}/{db_name}'


