import logging
from typing import Optional

import sentry_sdk
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LOG_LEVEL: str = 'INFO'
    SENTRY_DSN: Optional[str] = None


settings = Settings()

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] [%(name)s] - %(message)s',
    level=settings.LOG_LEVEL
)

sentry_sdk.init(dsn=settings.SENTRY_DSN, send_default_pii=True)
