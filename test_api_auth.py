#!/usr/bin/env python3
"""Test CoinGlass API authentication methods"""

import aiohttp
import asyncio
import json

API_KEY = "0e0cdf60bc4745aeb7e14532704f8a57"
BASE_URL = "https://open-api-v4.coinglass.com"

async def test_auth_header(session, header_name, endpoint="/api/futures/supported-coins"):
    """Test different authentication header names"""
    headers = {
        "accept": "application/json",
        header_name: API_KEY
    }
    
    print(f"\nTesting header: {header_name}")
    
    try:
        url = f"{BASE_URL}{endpoint}"
        async with session.get(url, headers=headers) as response:
            text = await response.text()
            print(f"Status: {response.status}")
            
            if response.status == 200:
                data = json.loads(text)
                if 'code' in data and data['code'] == '400':
                    print(f"❌ Authentication failed: {data.get('msg')}")
                elif 'code' in data and data['code'] == '0':
                    print(f"✅ SUCCESS! Authentication works")
                    print(f"Data preview: {json.dumps(data, indent=2)[:300]}...")
                    return True
                elif 'success' in data and data['success']:
                    print(f"✅ SUCCESS! Authentication works")
                    print(f"Data preview: {json.dumps(data, indent=2)[:300]}...")
                    return True
                elif 'data' in data:
                    print(f"✅ SUCCESS! Got data")
                    print(f"Data preview: {json.dumps(data, indent=2)[:300]}...")
                    return True
                else:
                    print(f"Unknown response format: {text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

async def test_working_endpoints(session, headers):
    """Test endpoints with proper auth"""
    print("\n" + "="*60)
    print("Testing endpoints with authentication")
    print("="*60)
    
    endpoints = [
        ("/api/futures/supported-coins", {}),
        ("/api/futures/liquidation/history", {"symbol": "BTC", "range": "12h"}),
        ("/api/futures/funding-rate/history", {"symbol": "BTC", "interval": "4h", "limit": 10}),
    ]
    
    for endpoint, params in endpoints:
        print(f"\n📍 Testing: {endpoint}")
        if params:
            print(f"   Params: {params}")
        
        try:
            url = f"{BASE_URL}{endpoint}"
            async with session.get(url, headers=headers, params=params) as response:
                text = await response.text()
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    data = json.loads(text)
                    if 'data' in data:
                        print(f"   ✅ Got data!")
                        if isinstance(data['data'], list):
                            print(f"   Data length: {len(data['data'])}")
                            if data['data']:
                                print(f"   First item: {json.dumps(data['data'][0], indent=2)[:200]}...")
                        else:
                            print(f"   Data type: {type(data['data'])}")
                            print(f"   Data preview: {json.dumps(data['data'], indent=2)[:200]}...")
                    else:
                        print(f"   Response: {json.dumps(data, indent=2)[:300]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def main():
    print("="*80)
    print("CoinGlass API Authentication Test")
    print("="*80)
    
    async with aiohttp.ClientSession() as session:
        # Test different header names
        header_names = [
            "CG-API-KEY",
            "coinglasskey",
            "Authorization",
            "X-API-KEY",
            "api-key",
            "apikey"
        ]
        
        working_header = None
        
        for header_name in header_names:
            if await test_auth_header(session, header_name):
                working_header = header_name
                break
        
        if working_header:
            print(f"\n🎯 Found working authentication header: {working_header}")
            
            # Test more endpoints with the working header
            headers = {
                "accept": "application/json",
                working_header: API_KEY
            }
            
            await test_working_endpoints(session, headers)
        else:
            print("\n❌ Could not find working authentication method")

if __name__ == "__main__":
    asyncio.run(main())