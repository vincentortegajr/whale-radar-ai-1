"""Health check API endpoints for WhaleRadar.ai"""

import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from src.utils.logger_setup import setup_logger
from src.utils.config import settings
from src.utils.monitoring import health_checker, performance_monitor
from src.api.coinglass_client import CoinGlassClient
from src.api.telegram_bot import TelegramNotifier
from src.utils.database import db

logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="WhaleRadar.ai Health API",
    version="1.0.0",
    description="Health monitoring and metrics for WhaleRadar.ai"
)


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "service": "WhaleRadar.ai"
    }


@app.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with all subsystem checks"""
    
    # Register health checks if not already done
    if not health_checker.checks:
        _register_health_checks()
    
    # Run all health checks
    results = await health_checker.run_checks()
    
    return results


@app.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get performance metrics"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_metrics": performance_monitor.get_system_metrics(),
        "api_statistics": performance_monitor.get_api_statistics(),
        "uptime_hours": (datetime.now(timezone.utc).timestamp() - performance_monitor.start_time) / 3600
    }


@app.get("/metrics/api/{endpoint}")
async def get_api_metrics(endpoint: str) -> Dict[str, Any]:
    """Get metrics for specific API endpoint"""
    stats = performance_monitor.get_api_statistics()
    
    if endpoint not in stats.get("by_endpoint", {}):
        raise HTTPException(status_code=404, detail=f"No metrics found for endpoint: {endpoint}")
    
    return {
        "endpoint": endpoint,
        "metrics": stats["by_endpoint"][endpoint],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def _register_health_checks():
    """Register all health check functions"""
    
    # Database check
    async def check_database():
        try:
            # Try to query recent signals
            signals = db.get_recent_signals(hours=1)
            return {"connected": True, "recent_signals": len(signals)}
        except Exception as e:
            raise Exception(f"Database error: {e}")
    
    # CoinGlass API check
    async def check_coinglass_api():
        try:
            async with CoinGlassClient() as client:
                # Try to fetch symbols
                symbols = await client.get_perpetual_symbols()
                return {"connected": True, "available_symbols": len(symbols)}
        except Exception as e:
            raise Exception(f"CoinGlass API error: {e}")
    
    # Telegram check
    async def check_telegram():
        try:
            notifier = TelegramNotifier()
            # Check bot info
            bot_info = await notifier.bot.get_me()
            return {"connected": True, "bot_username": bot_info.username}
        except Exception as e:
            raise Exception(f"Telegram error: {e}")
    
    # Disk space check
    def check_disk_space():
        import psutil
        disk_usage = psutil.disk_usage('/')
        
        if disk_usage.percent > 90:
            raise Exception(f"Disk space critical: {disk_usage.percent}% used")
        elif disk_usage.percent > 80:
            logger.warning(f"Disk space warning: {disk_usage.percent}% used")
            
        return {
            "used_percent": disk_usage.percent,
            "free_gb": disk_usage.free / (1024**3)
        }
    
    # Memory check
    def check_memory():
        import psutil
        memory = psutil.virtual_memory()
        
        if memory.percent > 90:
            raise Exception(f"Memory critical: {memory.percent}% used")
        elif memory.percent > 80:
            logger.warning(f"Memory warning: {memory.percent}% used")
            
        return {
            "used_percent": memory.percent,
            "available_mb": memory.available / (1024**2)
        }
    
    # Register all checks
    health_checker.register_check("database", check_database)
    health_checker.register_check("coinglass_api", check_coinglass_api)
    health_checker.register_check("telegram", check_telegram)
    health_checker.register_check("disk_space", check_disk_space)
    health_checker.register_check("memory", check_memory)


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Health API starting up...")
    _register_health_checks()


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Health API shutting down...")


def run_health_api(host: str = "0.0.0.0", port: int = 8080):
    """Run the health check API server"""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_health_api()