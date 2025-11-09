"""
Monitoring and Error Tracking with Sentry
"""
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.rq import RqIntegration


def init_sentry():
    """Initialize Sentry for error tracking"""
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")
    
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            traces_sample_rate=0.1,  # 10% of transactions
            profiles_sample_rate=0.1,  # 10% of profiling
            integrations=[
                FastApiIntegration(),
                RqIntegration(),
            ],
            # Send PII (personally identifiable information)
            send_default_pii=False,
            # Release tracking
            release=os.getenv("APP_VERSION", "1.0.0"),
        )
        return True
    return False


def capture_exception(error: Exception, context: dict = None):
    """Manually capture exception with context"""
    if context:
        sentry_sdk.set_context("custom", context)
    sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: dict = None):
    """Capture custom message"""
    if context:
        sentry_sdk.set_context("custom", context)
    sentry_sdk.capture_message(message, level=level)
