#!/usr/bin/env python3
"""Test actual API responses to fix parsing issues"""

import asyncio
import json
from src.api.coinglass_client import CoinGlassClient

async def test_api_responses():
    """Test actual API responses"""
    print("="*80)
    print("🔍 TESTING ACTUAL API RESPONSES")
    print("="*80)
    
    # Test 1: Get perpetual symbols
    print("\n1. Testing perpetual symbols endpoint...")
    try:
        async with CoinGlassClient() as client:
            response = await client._make_request("/api/futures/symbols", {})
            print(f"Response type: {type(response)}")
            print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            
            if isinstance(response, dict) and 'data' in response:
                data = response['data']
                print(f"Data type: {type(data)}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"First item: {data[0] if len(data) > 0 else 'Empty'}")
                    # Extract symbols correctly
                    symbols = [item['symbol'] if isinstance(item, dict) else item for item in data[:5]]
                    print(f"Symbols found: {symbols}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Coins markets endpoint
    print("\n2. Testing coins-markets endpoint...")
    try:
        async with CoinGlassClient() as client:
            response = await client._make_request("/api/futures/coins-markets", {"timeframe": "5m"})
            print(f"Response type: {type(response)}")
            
            if isinstance(response, dict):
                print(f"Response keys: {list(response.keys())}")
                if 'data' in response:
                    data = response['data']
                    print(f"Data type: {type(data)}")
                    if isinstance(data, list) and len(data) > 0:
                        print(f"First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
                        print(f"Sample data: {json.dumps(data[0], indent=2) if data else 'Empty'}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Liquidation map endpoint
    print("\n3. Testing liquidation map endpoint...")
    try:
        async with CoinGlassClient() as client:
            response = await client._make_request("/api/futures/liquidation/aggregated-map", 
                                                {"symbol": "BTC", "range": "24h"})
            print(f"Response type: {type(response)}")
            
            if isinstance(response, dict):
                print(f"Response keys: {list(response.keys())}")
                if 'data' in response:
                    data = response['data']
                    print(f"Data structure: {json.dumps(data, indent=2)[:500]}...")
                    
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: RSI endpoint
    print("\n4. Testing RSI endpoint...")
    try:
        async with CoinGlassClient() as client:
            response = await client._make_request("/api/futures/rsi/list", {"symbol": "BTC"})
            print(f"Response type: {type(response)}")
            
            if isinstance(response, dict):
                print(f"Response keys: {list(response.keys())}")
                if 'data' in response:
                    print(f"RSI data: {json.dumps(response['data'], indent=2)[:500]}...")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_responses())