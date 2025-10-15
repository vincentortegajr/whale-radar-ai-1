"""Data validation utilities for WhaleRadar.ai"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from src.utils.logger_setup import setup_logger

logger = setup_logger(__name__)


class APIResponse(BaseModel):
    """Base API response validation"""
    success: bool = Field(default=True)
    data: Any
    error: Optional[str] = None
    timestamp: Optional[datetime] = None


class PriceData(BaseModel):
    """Price data validation"""
    symbol: str
    price: float = Field(gt=0)
    timestamp: datetime
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0 or v > 1_000_000:  # Max $1M per coin reasonable
            raise ValueError(f'Invalid price: {v}')
        return v


class VolumeData(BaseModel):
    """Volume data validation"""
    symbol: str
    volume_24h: float = Field(ge=0)
    volume_change_pct: float = Field(ge=-100)  # Can't lose more than 100%
    
    @field_validator('volume_change_pct')
    @classmethod
    def validate_volume_change(cls, v):
        if v < -100 or v > 100000:  # 1000x max reasonable
            raise ValueError(f'Invalid volume change: {v}%')
        return v


class LiquidationData(BaseModel):
    """Liquidation data validation"""
    price: float = Field(gt=0)
    value_usd: float = Field(ge=0)
    type: str = Field(pattern='^(long|short)$')
    
    @field_validator('value_usd')
    @classmethod
    def validate_liquidation_value(cls, v):
        if v < 0 or v > 10_000_000_000:  # Max $10B reasonable
            raise ValueError(f'Invalid liquidation value: ${v}')
        return v


class RSIData(BaseModel):
    """RSI data validation"""
    symbol: str
    rsi: float = Field(ge=0, le=100)
    timeframe: str = Field(pattern='^(5m|15m|1h|4h|12h|1d|1w)$')
    
    @field_validator('rsi')
    @classmethod
    def validate_rsi(cls, v):
        if not 0 <= v <= 100:
            raise ValueError(f'Invalid RSI value: {v}')
        return v


def validate_symbol(symbol: str) -> bool:
    """Validate cryptocurrency symbol"""
    if not symbol:
        return False
    
    # Basic validation - alphanumeric, 2-10 chars
    if not symbol.isalnum() or len(symbol) < 2 or len(symbol) > 10:
        return False
    
    # Common patterns
    valid_patterns = [
        r'^[A-Z]{2,10}$',  # BTC, ETH, etc
        r'^[A-Z]{2,8}[0-9]{0,2}$',  # BTC1!, ETH2
    ]
    
    return True


def validate_api_response(response: Dict[str, Any], expected_fields: List[str]) -> bool:
    """Validate API response structure"""
    if not isinstance(response, dict):
        logger.error(f"Invalid response type: {type(response)}")
        return False
    
    # Check for error responses
    if response.get('error') or response.get('code') != 0:
        logger.error(f"API error: {response.get('error') or response.get('msg')}")
        return False
    
    # Check required fields
    for field in expected_fields:
        if field not in response:
            logger.error(f"Missing required field: {field}")
            return False
    
    return True


def validate_numerical_data(value: Union[int, float], min_val: float = None, 
                          max_val: float = None, name: str = "value") -> bool:
    """Validate numerical data within bounds"""
    try:
        num_val = float(value)
        
        if min_val is not None and num_val < min_val:
            logger.error(f"{name} too low: {num_val} < {min_val}")
            return False
            
        if max_val is not None and num_val > max_val:
            logger.error(f"{name} too high: {num_val} > {max_val}")
            return False
            
        # Check for NaN or infinity
        if not (-float('inf') < num_val < float('inf')):
            logger.error(f"{name} is NaN or infinity")
            return False
            
        return True
        
    except (TypeError, ValueError) as e:
        logger.error(f"Invalid numerical value for {name}: {value}")
        return False


def sanitize_input(text: str, max_length: int = 100) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove control characters
    sanitized = ''.join(char for char in text if ord(char) >= 32)
    
    # Truncate to max length
    sanitized = sanitized[:max_length]
    
    # Basic SQL injection prevention (though we use parameterized queries)
    dangerous_patterns = ['--', ';', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, '')
    
    return sanitized.strip()


def validate_timeframe(timeframe: str) -> bool:
    """Validate timeframe string"""
    valid_timeframes = ['5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w', '1M']
    return timeframe in valid_timeframes


def validate_percentage(value: float, name: str = "percentage") -> bool:
    """Validate percentage values"""
    return validate_numerical_data(value, min_val=-1000, max_val=10000, name=name)


class SignalValidator:
    """Validate trading signals before sending"""
    
    @staticmethod
    def validate_signal(signal) -> tuple[bool, List[str]]:
        """Validate a trading signal"""
        errors = []
        
        # Check basic fields
        if not signal.symbol or not validate_symbol(signal.symbol):
            errors.append("Invalid symbol")
            
        if signal.action not in ["LONG", "SHORT", "NEUTRAL"]:
            errors.append("Invalid action")
            
        if signal.confidence not in ["HIGH", "MEDIUM", "LOW"]:
            errors.append("Invalid confidence")
            
        # Validate numerical fields
        if not validate_numerical_data(signal.current_price, min_val=0, max_val=1_000_000):
            errors.append("Invalid current price")
            
        if not validate_numerical_data(signal.signal_strength, min_val=0, max_val=100):
            errors.append("Invalid signal strength")
            
        # Validate stop loss and take profits
        if signal.action != "NEUTRAL":
            if signal.action == "LONG":
                if signal.stop_loss >= signal.current_price:
                    errors.append("Stop loss must be below current price for LONG")
                if any(tp <= signal.current_price for tp in signal.take_profit_targets):
                    errors.append("Take profits must be above current price for LONG")
            else:  # SHORT
                if signal.stop_loss <= signal.current_price:
                    errors.append("Stop loss must be above current price for SHORT")
                if any(tp >= signal.current_price for tp in signal.take_profit_targets):
                    errors.append("Take profits must be below current price for SHORT")
        
        # Validate scale-in zones
        if signal.scale_in_zones:
            total_pct = sum(zone.get('position_pct', 0) for zone in signal.scale_in_zones)
            if not 95 <= total_pct <= 105:  # Allow 5% tolerance
                errors.append(f"Scale-in percentages must sum to ~100%, got {total_pct}%")
        
        return len(errors) == 0, errors


# Rate limiting validator
class RateLimiter:
    """Validate rate limits aren't exceeded"""
    
    def __init__(self, calls_per_second: int = 10):
        self.calls_per_second = calls_per_second
        self.call_times: List[float] = []
    
    def can_make_call(self) -> bool:
        """Check if we can make another API call"""
        import time
        now = time.time()
        
        # Remove calls older than 1 second
        self.call_times = [t for t in self.call_times if now - t < 1]
        
        # Check if we're under the limit
        return len(self.call_times) < self.calls_per_second
    
    def record_call(self):
        """Record that a call was made"""
        import time
        self.call_times.append(time.time())