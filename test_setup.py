#!/usr/bin/env python3
"""Test script to verify WhaleRadar.ai setup"""

import sys
import asyncio
from colorama import init, Fore, Style

init()  # Initialize colorama

def print_header():
    print(f"""
{Fore.CYAN}🐋 WhaleRadar.ai Setup Verification 🐋{Style.RESET_ALL}
{'='*50}
    """)

def check_import(module_name, display_name=None):
    """Check if a module can be imported"""
    display = display_name or module_name
    try:
        __import__(module_name)
        print(f"{Fore.GREEN}✅ {display}{Style.RESET_ALL}")
        return True
    except ImportError as e:
        print(f"{Fore.RED}❌ {display}: {e}{Style.RESET_ALL}")
        return False

async def check_api_connection():
    """Test CoinGlass API connection"""
    try:
        from src.api.coinglass_client import CoinGlassClient
        from src.utils.config import settings
        
        if not settings.coinglass_api_key:
            print(f"{Fore.YELLOW}⚠️  CoinGlass API key not configured{Style.RESET_ALL}")
            return False
            
        print(f"{Fore.CYAN}Testing CoinGlass API...{Style.RESET_ALL}")
        async with CoinGlassClient() as client:
            symbols = await client.get_perpetual_symbols()
            print(f"{Fore.GREEN}✅ CoinGlass API: Connected ({len(symbols)} perpetuals available){Style.RESET_ALL}")
            return True
    except Exception as e:
        print(f"{Fore.RED}❌ CoinGlass API: {e}{Style.RESET_ALL}")
        return False

async def check_telegram():
    """Test Telegram bot connection"""
    try:
        from src.api.telegram_bot import TelegramNotifier
        from src.utils.config import settings
        
        if not settings.telegram_bot_token:
            print(f"{Fore.YELLOW}⚠️  Telegram bot token not configured{Style.RESET_ALL}")
            return False
            
        print(f"{Fore.CYAN}Testing Telegram bot...{Style.RESET_ALL}")
        notifier = TelegramNotifier()
        # Just check if bot initializes, don't send message
        print(f"{Fore.GREEN}✅ Telegram bot: Initialized{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Telegram bot: {e}{Style.RESET_ALL}")
        return False

def check_environment():
    """Check environment configuration"""
    import os
    from pathlib import Path
    
    print(f"\n{Fore.BLUE}Environment Configuration:{Style.RESET_ALL}")
    
    # Check .env file
    env_path = Path(".env")
    if env_path.exists():
        print(f"{Fore.GREEN}✅ .env file found{Style.RESET_ALL}")
        
        # Check required variables
        required_vars = ["COINGLASS_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
        
        for var in required_vars:
            value = os.getenv(var)
            if value and value != "your_" + var.lower() + "_here":
                print(f"{Fore.GREEN}✅ {var}: Configured{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️  {var}: Not configured{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ .env file not found{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Copy .env.example to .env and add your credentials{Style.RESET_ALL}")
        return False
        
    return True

async def main():
    print_header()
    
    # Check Python version
    print(f"{Fore.BLUE}Python Version:{Style.RESET_ALL}")
    python_version = sys.version_info
    if python_version >= (3, 11):
        print(f"{Fore.GREEN}✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Python {python_version.major}.{python_version.minor} (3.11+ required){Style.RESET_ALL}")
        
    # Check dependencies
    print(f"\n{Fore.BLUE}Dependencies:{Style.RESET_ALL}")
    dependencies = [
        ("aiohttp", "aiohttp"),
        ("telegram", "python-telegram-bot"),
        ("pandas", "pandas"),
        ("colorlog", "colorlog"),
        ("pydantic", "pydantic"),
        ("dotenv", "python-dotenv"),
    ]
    
    all_deps_ok = True
    for module, display in dependencies:
        if not check_import(module, display):
            all_deps_ok = False
            
    if not all_deps_ok:
        print(f"\n{Fore.YELLOW}Run: pip install -r requirements.txt{Style.RESET_ALL}")
        return
        
    # Check project modules
    print(f"\n{Fore.BLUE}Project Modules:{Style.RESET_ALL}")
    modules = [
        "src.utils.config",
        "src.utils.logger",
        "src.utils.database",
        "src.api.coinglass_client",
        "src.api.telegram_bot",
        "src.indicators.visual_screener",
        "src.indicators.liquidation_analyzer",
        "src.indicators.rsi_heatmap",
        "src.strategies.master_strategy",
        "src.main"
    ]
    
    for module in modules:
        check_import(module)
        
    # Check environment
    env_ok = check_environment()
    
    if env_ok:
        # Test connections
        print(f"\n{Fore.BLUE}API Connections:{Style.RESET_ALL}")
        await check_api_connection()
        await check_telegram()
        
    # Summary
    print(f"\n{'='*50}")
    if env_ok:
        print(f"{Fore.GREEN}🚀 Setup verification complete!{Style.RESET_ALL}")
        print(f"\nTo start WhaleRadar.ai, run:")
        print(f"{Fore.CYAN}python -m src.main{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Please configure your environment first{Style.RESET_ALL}")
        print(f"\n1. Copy .env.example to .env")
        print(f"2. Add your API credentials")
        print(f"3. Run this test again")

if __name__ == "__main__":
    asyncio.run(main())