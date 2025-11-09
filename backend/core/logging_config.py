"""
Structured Logging Configuration
"""
import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging(level=logging.INFO):
    """Configure structured JSON logging"""
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        rename_fields={
            "asctime": "timestamp",
            "name": "logger",
            "levelname": "level",
            "message": "msg"
        }
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    
    return root_logger


# Request logging middleware
class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("api")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            method = scope["method"]
            path = scope["path"]
            
            self.logger.info(
                "Request started",
                extra={
                    "method": method,
                    "path": path,
                    "client": scope.get("client"),
                }
            )
        
        await self.app(scope, receive, send)
