#!/usr/bin/env python3
"""Test visual screener data format"""

import asyncio
import json
from src.api.coinglass_client import CoinGlassClient

async def test_screener_endpoints():
    """Test screener endpoints to see actual data format"""
    print("="*80)
    print("🔍 TESTING VISUAL SCREENER DATA FORMAT")
    print("="*80)
    
    async with CoinGlassClient() as client:
        # Test visual screener endpoints
        print("\n1. Testing Price vs OI screener...")
        try:
            data = await client.get_visual_screener_price_oi("5m")
            print(f"Response type: {type(data)}")
            if isinstance(data, dict):
                print(f"Response keys: {list(data.keys())}")
                if 'data' in data:
                    print(f"Data type: {type(data['data'])}")
                    if isinstance(data['data'], list) and data['data']:
                        print(f"First item: {json.dumps(data['data'][0], indent=2)[:300]}...")
                else:
                    print(f"Full response: {json.dumps(data, indent=2)[:300]}...")
            elif isinstance(data, list):
                print(f"List length: {len(data)}")
                if data:
                    print(f"First item: {json.dumps(data[0], indent=2)[:300]}...")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    
    # Test with raw request to see exact response
    print("\n2. Testing raw API request...")
    async with CoinGlassClient() as client:
        try:
            # Make raw request
            response = await client._make_request("/api/futures/coins-markets", {"timeframe": "5m"})
            print(f"Raw response type: {type(response)}")
            print(f"Raw response: {json.dumps(response, indent=2)[:500]}...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_screener_endpoints())