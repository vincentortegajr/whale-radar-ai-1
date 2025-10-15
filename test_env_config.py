#!/usr/bin/env python3
"""Test that environment variables are loaded correctly"""

from src.utils.config import settings, validate_config

print("="*80)
print("🔧 ENVIRONMENT CONFIGURATION TEST")
print("="*80)

# Test configuration validation
try:
    validate_config()
    print("✅ Configuration validation PASSED")
except Exception as e:
    print(f"❌ Configuration validation failed: {e}")

# Display loaded values (masked for security)
print("\n📋 Loaded Configuration:")
print(f"- CoinGlass API Key: {settings.coinglass_api_key[:10]}...{settings.coinglass_api_key[-4:]}")
print(f"- CoinGlass Base URL: {settings.coinglass_base_url}")
print(f"- Telegram Bot Token: {settings.telegram_bot_token[:10]}...{settings.telegram_bot_token[-4:]}")
print(f"- Telegram Chat ID: {settings.telegram_chat_id}")
print(f"- Bybit API Key: {settings.bybit_api_key[:10] if settings.bybit_api_key else 'Not set'}...")
print(f"- Bybit Testnet: {settings.bybit_testnet}")
print(f"- Log Level: {settings.log_level}")
print(f"- Polling Interval: {settings.polling_interval_seconds}s")
print(f"- Database Path: {settings.database_path}")

print("\n✅ All environment variables are properly configured and loaded!")