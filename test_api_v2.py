#!/usr/bin/env python3
"""Test CoinGlass API with different configurations"""

import aiohttp
import asyncio
import json

API_KEY = "0e0cdf60bcf57d8dd9f59b90b8fb4f29"

async def test_endpoint(session, base_url, endpoint, headers, params=None):
    """Test a single endpoint"""
    url = f"{base_url}{endpoint}"
    
    print(f"\nTesting: {url}")
    
    try:
        async with session.get(url, headers=headers, params=params) as response:
            text = await response.text()
            print(f"Status: {response.status}")
            
            if response.status == 200:
                print(f"✅ SUCCESS!")
                data = json.loads(text)
                print(f"Response preview: {text[:300]}...")
                return data
            else:
                print(f"❌ Failed: {text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("="*80)
    print("CoinGlass API Test - Finding correct endpoints")
    print("="*80)
    
    async with aiohttp.ClientSession() as session:
        # Test different header configurations
        headers_options = [
            {
                "coinglasskey": API_KEY,
                "Content-Type": "application/json"
            },
            {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            {
                "X-API-KEY": API_KEY,
                "Content-Type": "application/json"
            }
        ]
        
        base_urls = [
            "https://open-api.coinglass.com",
            "https://api.coinglass.com",
            "https://open-api-v4.coinglass.com"
        ]
        
        # Common endpoints to test
        endpoints = [
            "/public/v2/perpetual/markets",
            "/public/v2/funding",
            "/public/v2/liquidation",
            "/v1/perpetual/markets",
            "/v4/perpetual/markets",
            "/api/pro/v1/futures/liquidation/chart",
            "/api/pro/v1/futures/openInterest/chart",
            "/public/v2/indicator",
            "/api/futures/liquidation/map",
            "/api/pro/v1/coins/markets"
        ]
        
        # Test combinations
        for base_url in base_urls:
            print(f"\n{'='*40}")
            print(f"Testing base URL: {base_url}")
            print(f"{'='*40}")
            
            for headers in headers_options[:1]:  # Start with first header option
                print(f"\nUsing headers: {list(headers.keys())}")
                
                for endpoint in endpoints[:5]:  # Test first 5 endpoints
                    result = await test_endpoint(session, base_url, endpoint, headers)
                    if result:
                        print("🎯 Found working endpoint!")
                        break
                
                # If we found a working endpoint, test more
                if result:
                    break

if __name__ == "__main__":
    asyncio.run(main())