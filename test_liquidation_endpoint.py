#!/usr/bin/env python3
"""Test liquidation endpoint parameters"""

import aiohttp
import asyncio
import json

API_KEY = "0e0cdf60bc4745aeb7e14532704f8a57"
BASE_URL = "https://open-api-v4.coinglass.com"

async def test_liquidation_endpoint():
    """Test liquidation endpoint with different parameters"""
    print("="*80)
    print("🔍 TESTING LIQUIDATION HEATMAP ENDPOINT")
    print("="*80)
    
    headers = {
        "accept": "application/json",
        "CG-API-KEY": API_KEY
    }
    
    async with aiohttp.ClientSession() as session:
        # Test different parameter combinations
        test_cases = [
            {
                "name": "Basic coin parameter",
                "endpoint": "/api/futures/liquidation/aggregated-heatmap/model2",
                "params": {"coin": "BTC"}
            },
            {
                "name": "With exchange",
                "endpoint": "/api/futures/liquidation/aggregated-heatmap/model2",
                "params": {"coin": "BTC", "exchange": "BINANCE"}
            },
            {
                "name": "With time range",
                "endpoint": "/api/futures/liquidation/aggregated-heatmap/model2",
                "params": {"coin": "BTC", "startTime": "1760400000000", "endTime": "1760500000000"}
            },
            {
                "name": "With interval",
                "endpoint": "/api/futures/liquidation/aggregated-heatmap/model2",
                "params": {"coin": "BTC", "interval": "1h"}
            },
            {
                "name": "Try different endpoints",
                "endpoint": "/api/futures/liquidation/coin/map",
                "params": {"coin": "BTC"}
            }
        ]
        
        for test in test_cases:
            print(f"\n📍 Test: {test['name']}")
            print(f"   Endpoint: {test['endpoint']}")
            print(f"   Params: {test['params']}")
            
            try:
                url = f"{BASE_URL}{test['endpoint']}"
                async with session.get(url, headers=headers, params=test['params']) as response:
                    text = await response.text()
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        data = json.loads(text)
                        if 'data' in data:
                            print(f"   ✅ SUCCESS! Got data")
                            print(f"   Data preview: {json.dumps(data, indent=2)[:300]}...")
                        else:
                            print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                    else:
                        print(f"   ❌ Failed: {text[:200]}...")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_liquidation_endpoint())