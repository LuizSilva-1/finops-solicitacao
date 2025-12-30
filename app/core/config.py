from pydantic_settings import BaseSettings
from typing import Dict


class Settings(BaseSettings):
    database_url: str
    users_file: str = "data/users.json"
    secret_key: str = "change-me"
    allowed_services: list[str] = [
        "ebs_snapshot",
        "ec2",
        "elb",
        "s3",
        "rds_snapshot",
        "outro",
    ]
    allowed_regions: list[str] = ["sa-east-1", "us-east-1"]
    max_expiration_days: int = 365
    min_expiration_days: int = 1
    webhook_url: str | None = None
    webhook_channel: str | None = None
    webhook_username: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()
