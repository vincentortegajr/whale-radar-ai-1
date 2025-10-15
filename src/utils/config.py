"""Configuration management for WhaleRadar.ai"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # CoinGlass API
    coinglass_api_key: str = Field(default=os.getenv("COINGLASS_API_KEY", ""))
    coinglass_base_url: str = Field(default=os.getenv("COINGLASS_BASE_URL", "https://open-api-v4.coinglass.com"))
    
    # Telegram
    telegram_bot_token: str = Field(default=os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = Field(default=os.getenv("TELEGRAM_CHAT_ID", ""))
    
    # Bybit (Phase 3)
    bybit_api_key: Optional[str] = Field(default=os.getenv("BYBIT_API_KEY"))
    bybit_secret: Optional[str] = Field(default=os.getenv("BYBIT_SECRET"))
    bybit_testnet: bool = Field(default=os.getenv("BYBIT_TESTNET", "true").lower() == "true")
    
    # System Configuration
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    polling_interval_seconds: int = Field(default=int(os.getenv("POLLING_INTERVAL_SECONDS", "60")))
    scan_interval_minutes: int = Field(default=int(os.getenv("SCAN_INTERVAL_MINUTES", "5")))
    database_path: str = Field(default=os.getenv("DATABASE_PATH", "data/market_data.db"))
    max_alerts_per_hour: int = Field(default=int(os.getenv("MAX_ALERTS_PER_HOUR", "100")))
    
    # API Rate Limits (CoinGlass Pro)
    api_calls_per_second: int = Field(default=10)
    api_calls_per_minute: int = Field(default=600)
    
    # Trading Configuration
    default_leverage: int = Field(default=10)
    max_position_size_usd: float = Field(default=10000.0)
    default_risk_percent: float = Field(default=2.0)
    
    # Indicator Thresholds
    momentum_threshold_long: int = Field(default=70)
    momentum_threshold_short: int = Field(default=30)
    rsi_oversold: int = Field(default=30)
    rsi_overbought: int = Field(default=70)
    volume_spike_threshold: float = Field(default=200.0)  # 200% increase
    oi_spike_threshold: float = Field(default=50.0)  # 50% increase
    
    # Liquidation Analysis
    liquidation_ratio_threshold: float = Field(default=1.5)  # 1.5x more shorts than longs
    min_liquidation_value_usd: float = Field(default=1000000.0)  # $1M minimum
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Validate critical settings
def validate_config():
    """Validate that all required settings are present"""
    errors = []
    
    if not settings.coinglass_api_key:
        errors.append("COINGLASS_API_KEY is required")
    
    if not settings.telegram_bot_token:
        errors.append("TELEGRAM_BOT_TOKEN is required")
        
    if not settings.telegram_chat_id:
        errors.append("TELEGRAM_CHAT_ID is required")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True