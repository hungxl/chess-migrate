"""
Enhanced Game Logger

This module provides a comprehensive, colorful logging setup using loguru.
Features beautiful console output and structured file logging for the game.
"""

from pathlib import Path
from loguru import logger
import functools
from typing import Callable, Any

# Setup log directory
LOG_DIR = Path(__file__).parent
LOG_DIR.mkdir(exist_ok=True)

# Remove default handler
logger.remove()

# Enhanced console handler with beautiful colors and detailed formatting
# Only use log folders
# import sys
# logger.add(
#     sys.stderr,
#     level="DEBUG",
#     format=(
#         "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
#         "<level>{level: <8}</level> | "
#         "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
#         "<level>{message}</level>"
#     ),
#     colorize=True,
#     backtrace=True,
#     diagnose=True,
#     enqueue=True
# )

# Detailed file handler for debugging
logger.add(
    LOG_DIR / "chess_debug.log",
    level="DEBUG",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message} | "
        "Extra: {extra}"
    ),
    rotation="50 MB",  # Increased size to reduce rotation frequency
    retention="7 days",
    compression="zip",
    enqueue=True,  # Changed to True - uses background thread to avoid Windows locking
    backtrace=True,
    diagnose=True,
    serialize=False,
    catch=True  # Suppress rotation errors to prevent spam
)

# Game events log (INFO and above)
logger.add(
    LOG_DIR / "chess_game.log",
    level="INFO",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name} | "
        "{message}"
    ),
    rotation="50 MB",  # Increased size to reduce rotation frequency
    retention="30 days",
    compression="zip",
    enqueue=True,  # Changed to True - uses background thread to avoid Windows locking
    filter=lambda record: record["level"].name in ["INFO", "WARNING", "ERROR", "CRITICAL"],
    catch=True  # Suppress rotation errors to prevent spam
)

# Error-only log for critical issues
logger.add(
    LOG_DIR / "chess_errors.log",
    level="ERROR",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message} | "
        "Exception: {exception}"
    ),
    rotation="10 MB",  # Increased size to reduce rotation frequency
    retention="90 days",
    compression="zip",
    enqueue=True,  # Changed to True - uses background thread to avoid Windows locking
    backtrace=True,
    diagnose=True,
    catch=True  # Suppress rotation errors to prevent spam
)


def get_logger(name: str):
    """
    Get a logger instance for a module with enhanced context binding.

    Args:
        name: Name of the module/component (usually __name__)

    Returns:
        Logger instance with bound context
    
    Example:
        >>> log = get_logger(__name__)
        >>> log.info("Game started")
        >>> log.error("Failed to load level")
    """
    return logger.bind(name=name)


def log_function_call(log_level: str = "DEBUG"):
    """
    Decorator to automatically log function calls with parameters and return values.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Example:
        @log_function_call("INFO")
        def move_player(direction: str):
            return f"Moved {direction}"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_logger = get_logger(func.__module__)
            
            # Log function entry
            args_str = ", ".join(map(str, args[1:]))  # Skip 'self' parameter
            kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            params = ", ".join(filter(None, [args_str, kwargs_str]))
            
            getattr(func_logger, log_level.lower())(
                f"🚀 Calling {func.__name__}({params})"
            )
            
            try:
                result = func(*args, **kwargs)
                getattr(func_logger, log_level.lower())(
                    f"✅ {func.__name__} completed successfully"
                )
                return result
            except Exception as e:
                func_logger.error(
                    f"❌ {func.__name__} failed with {type(e).__name__}: {e}"
                )
                raise
                
        return wrapper
    return decorator


def log_performance(func: Callable) -> Callable:
    """
    Decorator to log function performance metrics.
    
    Example:
        @log_performance
        def generate_level():
            # Heavy computation
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        func_logger = get_logger(func.__module__)
        
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            func_logger.debug(
                f"⏱️  {func.__name__} executed in {execution_time:.2f}ms"
            )
            return result
        except Exception as e:
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            func_logger.error(
                f"💥 {func.__name__} failed after {execution_time:.2f}ms: {e}"
            )
            raise
            
    return wrapper


# Convenient logging shortcuts with emojis for better visibility
def log_game_event(logger, message: str, level: str = "INFO", **extra_data):
    """Log game events with emoji and extra context."""
    game_logger = logger or get_logger("GameEngine")
    emoji_map = {
        "DEBUG": "🔍",
        "INFO": "ℹ️ ",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "CRITICAL": "💀"
    }
    
    emoji = emoji_map.get(level.upper(), "📝")
    formatted_message = f"{emoji} {message}"
    
    getattr(game_logger, level.lower())(formatted_message, **extra_data)


def log_player_action(action: str, success: bool = True, **details):
    """Log player actions with context."""
    player_logger = logger or get_logger("Player")
    
    if success:
        player_logger.info(f"🎮 Player action: {action}", **details)
    else:
        player_logger.warning(f"🚫 Failed player action: {action}", **details)


# Enhanced error catching with automatic logging
def catch_and_log(
    level: str = "ERROR",
    message: str | None = None,
    reraise: bool = False,
    default_return: Any = None
):
    """
    Enhanced version of logger.catch with custom messages and return values.
    
    Args:
        level: Log level for caught exceptions
        message: Custom message prefix
        reraise: Whether to re-raise the exception
        default_return: Value to return if exception is caught and not re-raised
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_logger = get_logger(func.__module__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = message or f"Exception in {func.__name__}"
                getattr(func_logger, level.lower())(
                    f"💥 {error_msg}: {type(e).__name__}: {e}"
                )
                
                if reraise:
                    raise
                return default_return
                
        return wrapper
    return decorator
