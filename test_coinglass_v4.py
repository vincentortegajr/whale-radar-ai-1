#!/usr/bin/env python3
"""Test CoinGlass v4 API based on official documentation"""

import aiohttp
import asyncio
import json

API_KEY = "0e0cdf60bcf57d8dd9f59b90b8fb4f29"
BASE_URL = "https://open-api-v4.coinglass.com"

async def test_endpoint(session, endpoint, params=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "accept": "application/json",
        "CG-API-KEY": API_KEY  # Try different header formats
    }
    
    print(f"\nTesting: {endpoint}")
    
    try:
        async with session.get(url, headers=headers, params=params) as response:
            text = await response.text()
            print(f"Status: {response.status}")
            
            if response.status == 200:
                print(f"✅ SUCCESS!")
                try:
                    data = json.loads(text)
                    print(f"Response preview: {json.dumps(data, indent=2)[:500]}...")
                    return data
                except:
                    print(f"Response: {text[:500]}...")
                    return text
            else:
                print(f"❌ Failed: {text[:200]}...")
                
                # Try with different header
                headers["coinglasskey"] = API_KEY
                del headers["CG-API-KEY"]
                
                async with session.get(url, headers=headers, params=params) as response2:
                    if response2.status == 200:
                        text2 = await response2.text()
                        print(f"✅ SUCCESS with coinglasskey header!")
                        data = json.loads(text2)
                        print(f"Response preview: {json.dumps(data, indent=2)[:500]}...")
                        return data
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("="*80)
    print("CoinGlass v4 API Test - Based on Official Documentation")
    print("="*80)
    
    async with aiohttp.ClientSession() as session:
        # Test endpoints based on documentation structure
        endpoints_to_test = [
            # Futures endpoints
            "/api/futures/supported-coins",
            "/api/futures/coins/markets",
            "/api/futures/liquidation/chart",
            "/api/futures/liquidation/heatmap",
            "/api/futures/liquidation/history",
            "/api/futures/openInterest/chart",
            "/api/futures/openInterest/history", 
            "/api/futures/funding-rate/chart",
            "/api/futures/funding-rate/history",
            "/api/futures/long-short-ratio/chart",
            "/api/futures/long-short-ratio/history",
            
            # Indicator endpoints
            "/api/indicator/liquidation-heatmap",
            "/api/indicator/rsi-heatmap",
            "/api/indicator/market-overview",
            
            # Public endpoints (might not need auth)
            "/public/v2/perpetual/markets",
            "/public/v2/funding",
            "/public/v2/liquidation",
            
            # v1 endpoints (if still supported)
            "/v1/perpetual/markets",
            "/v1/liquidation/history"
        ]
        
        print("\nTesting various endpoint patterns...\n")
        
        successful_endpoints = []
        
        for endpoint in endpoints_to_test:
            result = await test_endpoint(session, endpoint)
            if result:
                successful_endpoints.append(endpoint)
                await asyncio.sleep(0.5)  # Rate limit
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        if successful_endpoints:
            print(f"\n✅ Found {len(successful_endpoints)} working endpoints:")
            for ep in successful_endpoints:
                print(f"   - {ep}")
        else:
            print("\n❌ No working endpoints found. The API might require:")
            print("   - Different authentication method")
            print("   - Different base URL")
            print("   - API key might not have required permissions")

if __name__ == "__main__":
    asyncio.run(main())