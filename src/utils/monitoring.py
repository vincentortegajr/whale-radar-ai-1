"""Performance monitoring and metrics for WhaleRadar.ai"""

import time
import psutil
import asyncio
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from functools import wraps
import statistics
from src.utils.logger_setup import setup_logger

logger = setup_logger(__name__)


@dataclass
class PerformanceMetric:
    """Container for performance metrics"""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class APICallMetric:
    """Metrics for API calls"""
    endpoint: str
    duration: float
    status_code: Optional[int]
    success: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PerformanceMonitor:
    """Monitors system performance and API metrics"""
    
    def __init__(self):
        self.api_calls: List[APICallMetric] = []
        self.metrics: Dict[str, List[float]] = {}
        self.start_time = time.time()
        
    def record_api_call(self, endpoint: str, duration: float, 
                       status_code: Optional[int] = None, success: bool = True):
        """Record an API call metric"""
        metric = APICallMetric(
            endpoint=endpoint,
            duration=duration,
            status_code=status_code,
            success=success
        )
        self.api_calls.append(metric)
        
        # Keep only last hour of data
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        self.api_calls = [m for m in self.api_calls if m.timestamp > cutoff]
        
    def record_metric(self, name: str, value: float):
        """Record a general metric"""
        if name not in self.metrics:
            self.metrics[name] = []
            
        self.metrics[name].append(value)
        
        # Keep only last 1000 values
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
            
    def get_api_statistics(self) -> Dict[str, Any]:
        """Get API call statistics"""
        if not self.api_calls:
            return {
                "total_calls": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "errors": 0
            }
            
        total_calls = len(self.api_calls)
        successful_calls = sum(1 for c in self.api_calls if c.success)
        failed_calls = total_calls - successful_calls
        
        durations = [c.duration for c in self.api_calls]
        avg_duration = statistics.mean(durations) if durations else 0
        
        # Group by endpoint
        by_endpoint = {}
        for call in self.api_calls:
            if call.endpoint not in by_endpoint:
                by_endpoint[call.endpoint] = {
                    "count": 0,
                    "avg_duration": 0,
                    "errors": 0
                }
            
            by_endpoint[call.endpoint]["count"] += 1
            by_endpoint[call.endpoint]["errors"] += 0 if call.success else 1
            
        # Calculate average durations per endpoint
        for endpoint in by_endpoint:
            endpoint_durations = [c.duration for c in self.api_calls if c.endpoint == endpoint]
            by_endpoint[endpoint]["avg_duration"] = statistics.mean(endpoint_durations)
            
        return {
            "total_calls": total_calls,
            "success_rate": (successful_calls / total_calls * 100) if total_calls > 0 else 0,
            "avg_duration": avg_duration,
            "errors": failed_calls,
            "by_endpoint": by_endpoint
        }
        
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_mb": psutil.virtual_memory().used / 1024 / 1024,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_hours": (time.time() - self.start_time) / 3600
        }
        
    def get_metric_statistics(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a specific metric"""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {
                "min": 0,
                "max": 0,
                "mean": 0,
                "median": 0,
                "std_dev": 0
            }
            
        values = self.metrics[metric_name]
        return {
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0
        }
        
    def log_summary(self):
        """Log performance summary"""
        api_stats = self.get_api_statistics()
        system_metrics = self.get_system_metrics()
        
        logger.info("=== Performance Summary ===")
        logger.info(f"API Calls: {api_stats['total_calls']} "
                   f"(Success: {api_stats['success_rate']:.1f}%, "
                   f"Avg: {api_stats['avg_duration']:.2f}s)")
        logger.info(f"System: CPU {system_metrics['cpu_percent']:.1f}%, "
                   f"Memory {system_metrics['memory_percent']:.1f}%, "
                   f"Uptime {system_metrics['uptime_hours']:.1f}h")
        
        # Log slowest endpoints
        if api_stats['by_endpoint']:
            slowest = sorted(api_stats['by_endpoint'].items(), 
                           key=lambda x: x[1]['avg_duration'], 
                           reverse=True)[:3]
            logger.info("Slowest endpoints:")
            for endpoint, stats in slowest:
                logger.info(f"  {endpoint}: {stats['avg_duration']:.2f}s avg")


def monitor_performance(monitor: PerformanceMonitor):
    """Decorator to monitor function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_metric(f"{func.__name__}_duration", duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_metric(f"{func.__name__}_error_duration", duration)
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_metric(f"{func.__name__}_duration", duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_metric(f"{func.__name__}_error_duration", duration)
                raise
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def monitor_api_call(monitor: PerformanceMonitor, endpoint: str):
    """Decorator to monitor API calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            status_code = None
            
            try:
                result = await func(*args, **kwargs)
                success = True
                
                # Try to extract status code if available
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                elif isinstance(result, dict) and 'status_code' in result:
                    status_code = result['status_code']
                    
                return result
                
            except Exception as e:
                # Try to extract status code from exception
                if hasattr(e, 'status_code'):
                    status_code = e.status_code
                raise
                
            finally:
                duration = time.time() - start_time
                monitor.record_api_call(endpoint, duration, status_code, success)
                
        return wrapper
    return decorator


class HealthChecker:
    """Performs health checks on the system"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.checks: Dict[str, Callable] = {}
        
    def register_check(self, name: str, check_func: Callable) -> None:
        """Register a health check"""
        self.checks[name] = check_func
        
    async def run_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all health checks"""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                start_time = time.time()
                
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                    
                duration = time.time() - start_time
                
                results[name] = {
                    "status": "healthy",
                    "duration": duration,
                    "result": result
                }
                
            except Exception as e:
                results[name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "duration": time.time() - start_time
                }
                
        # Overall status
        all_healthy = all(r["status"] == "healthy" for r in results.values())
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": results,
            "system_metrics": self.monitor.get_system_metrics(),
            "api_statistics": self.monitor.get_api_statistics()
        }


# Global monitor instance
performance_monitor = PerformanceMonitor()
health_checker = HealthChecker(performance_monitor)