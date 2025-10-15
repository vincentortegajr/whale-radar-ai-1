#!/usr/bin/env python3
"""Test actual CoinGlass API responses to ensure our code matches reality"""

import asyncio
import json
from src.api.coinglass_client import CoinGlassClient
from src.utils.config import settings
from src.utils.logger_setup import setup_logger

logger = setup_logger(__name__)


async def test_api_endpoints():
    """Test each API endpoint to verify response structure"""
    
    print("=" * 60)
    print("🔬 TESTING ACTUAL COINGLASS API RESPONSES")
    print("=" * 60)
    
    if not settings.coinglass_api_key:
        print("❌ No API key configured!")
        return
        
    async with CoinGlassClient() as client:
        # Test 1: Get perpetual symbols
        print("\n1. Testing get_perpetual_symbols...")
        try:
            symbols = await client.get_perpetual_symbols()
            print(f"✅ Got {len(symbols)} symbols")
            print(f"   Sample symbols: {symbols[:5]}")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        # Test 2: Visual Screener - Price vs OI
        print("\n2. Testing visual screener (Price vs OI)...")
        try:
            data = await client.get_visual_screener_price_oi(timeframe="1h")
            print(f"✅ Got {len(data)} results")
            if data:
                print("   Sample data structure:")
                print(json.dumps(data[0], indent=2)[:500] + "...")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        # Test 3: Liquidation Heatmap
        print("\n3. Testing liquidation heatmap for BTC...")
        try:
            data = await client.get_liquidation_heatmap("BTC", model=2, timeframe="24h")
            print("✅ Got liquidation data")
            print("   Data structure:")
            print(json.dumps(data, indent=2)[:500] + "...")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        # Test 4: RSI Heatmap
        print("\n4. Testing RSI heatmap...")
        try:
            data = await client.get_rsi_heatmap(timeframe="1h", top=10)
            print(f"✅ Got RSI data for {len(data)} coins")
            if data:
                print("   Sample RSI data:")
                print(json.dumps(data[0], indent=2)[:300] + "...")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        # Test 5: Market Overview
        print("\n5. Testing market overview...")
        try:
            data = await client.get_market_overview()
            print("✅ Got market overview")
            print("   Data structure:")
            print(json.dumps(data, indent=2)[:500] + "...")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        print("\n" + "=" * 60)
        print("🔬 API ENDPOINT TESTING COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_api_endpoints())