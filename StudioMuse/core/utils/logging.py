import logging
import os
from enum import Enum, auto
from typing import Optional
from gi.repository import Gimp

class LogLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    DEBUG = auto()

def setup_studio_logger(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name or "studiomuse")
    
    if logger.handlers:
        return logger

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    
    handlers = [logging.StreamHandler()]
    try:
        log_path = os.path.join(os.path.dirname(__file__), '../../logs/studiomuse.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        handlers.append(logging.FileHandler(log_path))
    except OSError:
        pass

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    
    return logger

def _log(message: str, level: LogLevel, logger_name: Optional[str] = None, user_visible: bool = True):
    logger = logging.getLogger(logger_name or "studiomuse")
    
    # Developer logging
    getattr(logger, level.name.lower())(message)
    
    # User logging
    if user_visible and level != LogLevel.DEBUG:
        prefix = f"{level.name.capitalize()}: " if level in (LogLevel.ERROR, LogLevel.WARNING) else ""
        Gimp.message(f"{prefix}{message}")

def log_error(message: str, exception: Optional[Exception] = None, logger_name: Optional[str] = None, user_visible: bool = True):
    _log(f"{message}: {str(exception)}" if exception else message, LogLevel.ERROR, logger_name, user_visible)

def log_warning(message: str, logger_name: Optional[str] = None, user_visible: bool = True):
    _log(message, LogLevel.WARNING, logger_name, user_visible)

def log_info(message: str, logger_name: Optional[str] = None, user_visible: bool = True):
    _log(message, LogLevel.INFO, logger_name, user_visible)

def log_debug(message: str, logger_name: Optional[str] = None):
    _log(message, LogLevel.DEBUG, logger_name, False)

root_logger = setup_studio_logger()
