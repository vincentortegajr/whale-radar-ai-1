#!/usr/bin/env python3
"""Test CoinGlass PRO endpoints ($900/month tier) to match exact functionality"""

import asyncio
import json
import aiohttp
from datetime import datetime
from src.utils.config import settings
from src.utils.logger_setup import setup_logger

logger = setup_logger(__name__)


class CoinGlassProTester:
    """Test actual PRO API endpoints based on the visual interface"""
    
    def __init__(self):
        self.api_key = settings.coinglass_api_key
        self.base_url = "https://api.coinglass.com/api/pro/v1"  # PRO API base URL
        self.headers = {
            "coinglasskey": self.api_key,
            "Content-Type": "application/json"
        }
        
    async def test_all_pro_endpoints(self):
        """Test all PRO endpoints shown in the interface"""
        print("=" * 80)
        print("🔥 TESTING COINGLASS PRO ENDPOINTS ($900/month)")
        print("=" * 80)
        
        async with aiohttp.ClientSession() as session:
            # 1. VISUAL SCREENERS - All 3 types shown in STEP 1
            await self._test_visual_screeners(session)
            
            # 2. LIQUIDATION HEATMAP MODEL 2 - STEP 2
            await self._test_liquidation_heatmap(session)
            
            # 3. RSI HEATMAP - STEP 3
            await self._test_rsi_heatmap(session)
            
            # 4. WHALE ALERTS
            await self._test_whale_alerts(session)
            
            # 5. ON-CHAIN FLOW
            await self._test_onchain_flow(session)
            
    async def _test_visual_screeners(self, session):
        """Test all 3 visual screener types"""
        print("\n📊 STEP 1: VISUAL SCREENERS")
        print("-" * 40)
        
        screeners = [
            ("price-oi", "Price vs Open Interest Change"),
            ("price-volume", "Price vs Volume Change"),
            ("volume-oi", "Volume vs Open Interest Change")
        ]
        
        for endpoint, name in screeners:
            try:
                url = f"{self.base_url}/futures/visual-screener/{endpoint}"
                params = {
                    "interval": "5m",  # 5-minute intervals as you specified
                    "limit": 50
                }
                
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {name}:")
                        print(f"   - Status: {data.get('success', False)}")
                        print(f"   - Data points: {len(data.get('data', []))}")
                        
                        if data.get('data'):
                            sample = data['data'][0]
                            print(f"   - Sample: {json.dumps(sample, indent=2)[:200]}...")
                    else:
                        print(f"❌ {name}: HTTP {response.status}")
                        
            except Exception as e:
                print(f"❌ {name}: {str(e)}")
                
    async def _test_liquidation_heatmap(self, session):
        """Test liquidation heatmap Model 2"""
        print("\n💧 STEP 2: LIQUIDATION HEATMAP MODEL 2")
        print("-" * 40)
        
        try:
            # Test for BTC as shown in the image
            url = f"{self.base_url}/futures/liquidation_map_chart"
            params = {
                "symbol": "BTC",
                "interval": "0"  # Aggregated data
            }
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Liquidation Heatmap Model 2:")
                    print(f"   - Success: {data.get('success', False)}")
                    print(f"   - Price levels: {len(data.get('data', {}).get('priceList', []))}")
                    
                    # Check for long/short liquidation data
                    if 'data' in data:
                        liq_data = data['data']
                        print(f"   - Has long liquidations: {'longLiquidationList' in liq_data}")
                        print(f"   - Has short liquidations: {'shortLiquidationList' in liq_data}")
                else:
                    print(f"❌ Liquidation Heatmap: HTTP {response.status}")
                    
        except Exception as e:
            print(f"❌ Liquidation Heatmap: {str(e)}")
            
    async def _test_rsi_heatmap(self, session):
        """Test RSI heatmap endpoint"""
        print("\n📈 STEP 3: RSI HEATMAP")
        print("-" * 40)
        
        try:
            url = f"{self.base_url}/indicator/market_rsi"
            params = {
                "interval": "1h",
                "limit": 100  # Top 100 as shown
            }
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ RSI Heatmap:")
                    print(f"   - Success: {data.get('success', False)}")
                    print(f"   - Coins analyzed: {len(data.get('data', []))}")
                    
                    if data.get('data'):
                        # Count RSI statuses
                        statuses = {}
                        for coin in data['data']:
                            status = self._get_rsi_status(coin.get('rsi', 50))
                            statuses[status] = statuses.get(status, 0) + 1
                            
                        print("   - RSI Distribution:")
                        for status, count in statuses.items():
                            print(f"     • {status}: {count}")
                else:
                    print(f"❌ RSI Heatmap: HTTP {response.status}")
                    
        except Exception as e:
            print(f"❌ RSI Heatmap: {str(e)}")
            
    async def _test_whale_alerts(self, session):
        """Test whale alert endpoint"""
        print("\n🐋 WHALE ALERTS")
        print("-" * 40)
        
        try:
            url = f"{self.base_url}/whale_alert/list"
            params = {
                "limit": 20
            }
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Whale Alerts:")
                    print(f"   - Success: {data.get('success', False)}")
                    print(f"   - Recent alerts: {len(data.get('data', []))}")
                    
                    if data.get('data'):
                        alert = data['data'][0]
                        print(f"   - Latest: {alert.get('coin')} - ${alert.get('amount', 0):,.0f}")
                else:
                    print(f"❌ Whale Alerts: HTTP {response.status}")
                    
        except Exception as e:
            print(f"❌ Whale Alerts: {str(e)}")
            
    async def _test_onchain_flow(self, session):
        """Test on-chain flow endpoint"""
        print("\n🔗 ON-CHAIN FLOW")
        print("-" * 40)
        
        try:
            url = f"{self.base_url}/exchange_flows/data_list"
            params = {
                "exchange": "all",
                "type": "btc"
            }
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ On-chain Flow:")
                    print(f"   - Success: {data.get('success', False)}")
                    
                    if data.get('data'):
                        flow_data = data['data']
                        print(f"   - Inflow: {flow_data.get('inflow', 0)}")
                        print(f"   - Outflow: {flow_data.get('outflow', 0)}")
                        print(f"   - Net flow: {flow_data.get('netflow', 0)}")
                else:
                    print(f"❌ On-chain Flow: HTTP {response.status}")
                    
        except Exception as e:
            print(f"❌ On-chain Flow: {str(e)}")
            
    def _get_rsi_status(self, rsi):
        """Get RSI status based on value"""
        if rsi >= 70:
            return "OVERBOUGHT"
        elif rsi >= 60:
            return "STRONG"
        elif rsi >= 40:
            return "NEUTRAL"
        elif rsi >= 30:
            return "WEAK"
        else:
            return "OVERSOLD"
            
    async def verify_api_key(self, session):
        """Verify API key is valid and PRO tier"""
        try:
            url = f"{self.base_url}/account/info"
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print("\n🔑 API KEY VERIFICATION:")
                    print(f"   - Valid: {data.get('success', False)}")
                    print(f"   - Tier: {data.get('data', {}).get('plan', 'Unknown')}")
                    print(f"   - Credits: {data.get('data', {}).get('credits', 'Unknown')}")
                    return True
                else:
                    print(f"\n❌ API Key Invalid: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"\n❌ API Key Error: {str(e)}")
            return False


async def main():
    """Run all PRO endpoint tests"""
    tester = CoinGlassProTester()
    
    # First verify API key
    async with aiohttp.ClientSession() as session:
        valid = await tester.verify_api_key(session)
        if not valid:
            print("\n⚠️  Please check your API key!")
            return
    
    # Test all endpoints
    await tester.test_all_pro_endpoints()
    
    print("\n" + "=" * 80)
    print("✅ PRO ENDPOINT TESTING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())