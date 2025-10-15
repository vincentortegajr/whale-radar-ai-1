"""Comprehensive error handling for WhaleRadar.ai"""

import sys
import traceback
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timezone
from functools import wraps
import asyncio
from src.utils.logger_setup import setup_logger

logger = setup_logger(__name__)


class WhaleRadarError(Exception):
    """Base exception for WhaleRadar.ai"""
    pass


class APIError(WhaleRadarError):
    """API related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class ConfigurationError(WhaleRadarError):
    """Configuration related errors"""
    pass


class DataValidationError(WhaleRadarError):
    """Data validation errors"""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        message = f"Rate limit exceeded. Retry after {retry_after} seconds" if retry_after else "Rate limit exceeded"
        super().__init__(message, status_code=429)


class TelegramError(WhaleRadarError):
    """Telegram bot related errors"""
    pass


def handle_errors(func: Callable) -> Callable:
    """Decorator for synchronous error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except WhaleRadarError:
            raise  # Re-raise our custom errors
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise WhaleRadarError(f"Unexpected error: {str(e)}") from e
    return wrapper


def async_handle_errors(func: Callable) -> Callable:
    """Decorator for asynchronous error handling"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            logger.info(f"{func.__name__} was cancelled")
            raise
        except WhaleRadarError:
            raise  # Re-raise our custom errors
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise WhaleRadarError(f"Unexpected error: {str(e)}") from e
    return wrapper


class ErrorRecovery:
    """Handles error recovery strategies"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, datetime] = {}
        self.max_errors = 5
        self.error_window = 300  # 5 minutes
        
    def record_error(self, error_type: str):
        """Record an error occurrence"""
        now = datetime.now(timezone.utc)
        
        # Clean old errors
        self._clean_old_errors()
        
        # Record new error
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
            
        self.error_counts[error_type] += 1
        self.last_errors[error_type] = now
        
        logger.warning(f"Error recorded: {error_type} (count: {self.error_counts[error_type]})")
        
    def should_circuit_break(self, error_type: str) -> bool:
        """Check if circuit breaker should activate"""
        self._clean_old_errors()
        return self.error_counts.get(error_type, 0) >= self.max_errors
        
    def _clean_old_errors(self):
        """Remove errors outside the time window"""
        now = datetime.now(timezone.utc)
        
        for error_type in list(self.error_counts.keys()):
            if error_type in self.last_errors:
                time_diff = (now - self.last_errors[error_type]).total_seconds()
                if time_diff > self.error_window:
                    del self.error_counts[error_type]
                    del self.last_errors[error_type]
                    
    def reset_error_count(self, error_type: str):
        """Reset error count for a specific type"""
        if error_type in self.error_counts:
            del self.error_counts[error_type]
        if error_type in self.last_errors:
            del self.last_errors[error_type]


class RetryStrategy:
    """Implements retry logic with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        
    async def execute_with_retry(self, func: Callable, *args, **kwargs):
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
                
            except RateLimitError as e:
                # Use rate limit retry_after if available
                delay = e.retry_after or self._calculate_delay(attempt)
                logger.warning(f"Rate limited. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                last_exception = e
                
            except APIError as e:
                if e.status_code and 500 <= e.status_code < 600:
                    # Retry on server errors
                    delay = self._calculate_delay(attempt)
                    logger.warning(f"Server error {e.status_code}. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    last_exception = e
                else:
                    # Don't retry on client errors
                    raise
                    
            except (asyncio.TimeoutError, ConnectionError) as e:
                # Retry on network errors
                delay = self._calculate_delay(attempt)
                logger.warning(f"Network error. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                last_exception = e
                
            except Exception as e:
                # Don't retry on unexpected errors
                logger.error(f"Unexpected error: {e}")
                raise
                
        # All retries exhausted
        raise WhaleRadarError(f"Max retries ({self.max_retries}) exceeded") from last_exception
        
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        # Add jitter to prevent thundering herd
        import random
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter


def setup_global_error_handler():
    """Setup global exception handler"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
    sys.excepthook = handle_exception


# Global instances
error_recovery = ErrorRecovery()
retry_strategy = RetryStrategy()


async def safe_execute(func: Callable, *args, **kwargs) -> Optional[Any]:
    """Safely execute a function with full error handling"""
    try:
        return await retry_strategy.execute_with_retry(func, *args, **kwargs)
    except Exception as e:
        error_type = type(e).__name__
        error_recovery.record_error(error_type)
        
        if error_recovery.should_circuit_break(error_type):
            logger.error(f"Circuit breaker activated for {error_type}")
            raise WhaleRadarError(f"Too many {error_type} errors. Circuit breaker activated.")
        
        raise