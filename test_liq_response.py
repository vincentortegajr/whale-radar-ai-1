#!/usr/bin/env python3
"""Test liquidation response"""

import asyncio
from src.api.coinglass_client import CoinGlassClient

async def test_liquidation():
    async with CoinGlassClient() as client:
        response = await client.get_liquidation_heatmap("BTC", model=2, timeframe="24h")
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        
        # Try with exchange parameter
        response2 = await client._make_request("/api/futures/liquidation/aggregated-heatmap/model2", 
                                             {"symbol": "BTC", "exchange": "BINANCE"})
        print(f"\nWith exchange: {response2}")

if __name__ == "__main__":
    asyncio.run(test_liquidation())