"""CoinGlass PRO API Endpoint Mappings - $900/month tier"""

# Base URL for PRO API
PRO_BASE_URL = "https://api.coinglass.com/api/pro/v1"

# Visual Screener Endpoints (STEP 1)
VISUAL_SCREENER_ENDPOINTS = {
    "price_oi": "/futures/visual-screener/price-oi",
    "price_volume": "/futures/visual-screener/price-volume", 
    "volume_oi": "/futures/visual-screener/volume-oi"
}

# Liquidation Heatmap Endpoints (STEP 2)
LIQUIDATION_ENDPOINTS = {
    "heatmap": "/futures/liquidation_map_chart",  # Model 2
    "aggregate": "/futures/liquidation_aggregate",
    "history": "/futures/liquidation_history"
}

# RSI Heatmap Endpoints (STEP 3)
RSI_ENDPOINTS = {
    "heatmap": "/indicator/market_rsi",
    "detail": "/indicator/coin_rsi"
}

# Whale Alert Endpoints
WHALE_ENDPOINTS = {
    "alerts": "/whale_alert/list",
    "large_transfers": "/whale_alert/large_transfer"
}

# On-chain Flow Endpoints  
ONCHAIN_ENDPOINTS = {
    "exchange_flows": "/exchange_flows/data_list",
    "btc_flows": "/bitcoin/flow",
    "eth_flows": "/ethereum/flow"
}

# Market Overview
MARKET_ENDPOINTS = {
    "overview": "/market/overview",
    "perpetual_list": "/futures/perpetual_list"
}

# Parameters mapping for PRO API
PARAM_MAPPINGS = {
    "timeframe": "interval",  # PRO API uses 'interval' not 'timeframe'
    "top": "limit",          # PRO API uses 'limit' not 'top'
}