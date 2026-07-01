"""
utils/logger.py — Structured JSON logging with automatic sanitization.
"""
import json
import logging
import os
import sys
from typing import Any, Dict, List, Union

from pythonjsonlogger import jsonlogger

# Sensitive keys to redact
SENSITIVE_KEYS = {
    'api_key', 'private_key', 'token', 'password', 'secret',
    'signature', 'credential', 'auth', 'authorization'
}

def sanitize_log(data: Any) -> Any:
    """Recursively remove sensitive keys from log data."""
    if isinstance(data, dict):
        return {
            k: '***REDACTED***' if k.lower() in SENSITIVE_KEYS else sanitize_log(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [sanitize_log(item) for item in data]
    return data

class SanitizingJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter that sanitizes sensitive data."""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Sanitize extra fields
        for key in list(log_record.keys()):
            if key not in ['asctime', 'levelname', 'name', 'message']:
                log_record[key] = sanitize_log(log_record[key])

def setup_logger(
    name: str = None,
    level: int = logging.INFO,
    json_format: bool = True,
) -> logging.Logger:
    """
    Setup structured logger with sanitization.
    
    Args:
        name: Logger name
        level: Logging level
        json_format: Use JSON format (True) or plain text (False)
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        # JSON format with sanitization
        formatter = SanitizingJsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s',
            rename_fields={
                'asctime': 'timestamp',
                'levelname': 'level',
                'name': 'logger'
            }
        )
    else:
        # Plain text format
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

def log_api_response(
    logger: logging.Logger,
    level: int,
    message: str,
    response: Dict,
    **kwargs
):
    """Log API response with automatic sanitization."""
    sanitized = sanitize_log(response)
    logger.log(level, message, extra={'response': sanitized, **kwargs})

def log_error_with_context(
    logger: logging.Logger,
    message: str,
    error: Exception,
    context: Dict = None
):
    """Log error with full context."""
    logger.error(
        message,
        extra={
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': sanitize_log(context or {})
        },
        exc_info=True
    )

# Convenience function for quick setup
def init_logging(json_format: bool = True) -> None:
    """Initialize root logger with sanitization."""
    root_logger = setup_logger(None, logging.INFO, json_format)
    
    # Suppress noisy loggers
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    root_logger.info("✅ Logging initialized", extra={'format': 'JSON' if json_format else 'text'})
