#!/usr/bin/env python3
"""Simple API test to check CoinGlass v4 endpoints"""

import aiohttp
import asyncio
import json

API_KEY = "0e0cdf60bcf57d8dd9f59b90b8fb4f29"

async def test_endpoint(session, endpoint, params=None):
    """Test a single endpoint"""
    url = f"https://open-api.coinglass.com{endpoint}"
    headers = {
        "coinglasskey": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting: {endpoint}")
    print(f"URL: {url}")
    
    try:
        async with session.get(url, headers=headers, params=params) as response:
            text = await response.text()
            print(f"Status: {response.status}")
            print(f"Response: {text[:200]}...")
            
            if response.status == 200:
                data = json.loads(text)
                print(f"Response type: {type(data)}")
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())}")
                return data
            
    except Exception as e:
        print(f"Error: {e}")

async def main():
    print("="*80)
    print("CoinGlass API v4 Endpoint Test")
    print("="*80)
    
    async with aiohttp.ClientSession() as session:
        # Test common endpoints from v4 docs
        
        # 1. Try market data endpoint
        await test_endpoint(session, "/api/futures/coins-markets")
        
        # 2. Try funding rate
        await test_endpoint(session, "/api/futures/funding-rate/ohlc-history", {"symbol": "BTC", "type": "U"})
        
        # 3. Try liquidation history
        await test_endpoint(session, "/api/futures/liquidation/history", {"symbol": "BTC", "range": "12h"})
        
        # 4. Try open interest
        await test_endpoint(session, "/api/futures/openInterest/ohlc", {"symbol": "BTC"})
        
        # 5. Try perpetual markets (correct endpoint for symbols)
        await test_endpoint(session, "/api/perpetual/markets")
        
        # 6. Try spot supported coins
        await test_endpoint(session, "/api/spot/supported-coins")

if __name__ == "__main__":
    asyncio.run(main())