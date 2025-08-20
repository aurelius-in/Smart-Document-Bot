import time
import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import psutil
import os

from .config import settings

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_metrics = deque(maxlen=max_history)
        self.error_metrics = deque(maxlen=max_history)
        self.performance_metrics = deque(maxlen=max_history)
        self.agent_metrics = deque(maxlen=max_history)
        self.lock = threading.Lock()
        
        # Initialize counters
        self.total_requests = 0
        self.total_errors = 0
        self.total_agent_executions = 0
        
        # Start background metrics collection
        self._start_background_collection()
    
    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Record a request metric"""
        metric = {
            "timestamp": time.time(),
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
            "datetime": datetime.utcnow().isoformat()
        }
        
        with self.lock:
            self.request_metrics.append(metric)
            self.total_requests += 1
            
            if status_code >= 400:
                self.error_metrics.append(metric)
                self.total_errors += 1
    
    def record_agent_execution(self, agent_name: str, duration: float, success: bool, 
                              confidence: Optional[float] = None, error: Optional[str] = None):
        """Record an agent execution metric"""
        metric = {
            "timestamp": time.time(),
            "agent_name": agent_name,
            "duration": duration,
            "success": success,
            "confidence": confidence,
            "error": error,
            "datetime": datetime.utcnow().isoformat()
        }
        
        with self.lock:
            self.agent_metrics.append(metric)
            self.total_agent_executions += 1
    
    def record_performance_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a performance metric"""
        metric = {
            "timestamp": time.time(),
            "metric_name": metric_name,
            "value": value,
            "tags": tags or {},
            "datetime": datetime.utcnow().isoformat()
        }
        
        with self.lock:
            self.performance_metrics.append(metric)
    
    def get_request_stats(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get request statistics for the specified time window"""
        cutoff_time = time.time() - (window_minutes * 60)
        
        with self.lock:
            recent_requests = [
                req for req in self.request_metrics 
                if req["timestamp"] >= cutoff_time
            ]
            
            if not recent_requests:
                return {
                    "total_requests": 0,
                    "avg_response_time": 0,
                    "error_rate": 0,
                    "status_codes": {},
                    "endpoints": {}
                }
            
            # Calculate statistics
            total_requests = len(recent_requests)
            avg_response_time = sum(req["duration"] for req in recent_requests) / total_requests
            error_count = len([req for req in recent_requests if req["status_code"] >= 400])
            error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
            
            # Status code distribution
            status_codes = defaultdict(int)
            for req in recent_requests:
                status_codes[req["status_code"]] += 1
            
            # Endpoint distribution
            endpoints = defaultdict(int)
            for req in recent_requests:
                endpoints[req["path"]] += 1
            
            return {
                "total_requests": total_requests,
                "avg_response_time": avg_response_time,
                "error_rate": error_rate,
                "status_codes": dict(status_codes),
                "endpoints": dict(endpoints),
                "window_minutes": window_minutes
            }
    
    def get_agent_stats(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get agent execution statistics"""
        cutoff_time = time.time() - (window_minutes * 60)
        
        with self.lock:
            recent_executions = [
                exec_ for exec_ in self.agent_metrics 
                if exec_["timestamp"] >= cutoff_time
            ]
            
            if not recent_executions:
                return {
                    "total_executions": 0,
                    "success_rate": 0,
                    "avg_duration": 0,
                    "agents": {}
                }
            
            # Calculate statistics
            total_executions = len(recent_executions)
            successful_executions = len([exec_ for exec_ in recent_executions if exec_["success"]])
            success_rate = (successful_executions / total_executions) * 100 if total_executions > 0 else 0
            avg_duration = sum(exec_["duration"] for exec_ in recent_executions) / total_executions
            
            # Agent-specific statistics
            agents = defaultdict(lambda: {"executions": 0, "successes": 0, "total_duration": 0})
            for exec_ in recent_executions:
                agent_name = exec_["agent_name"]
                agents[agent_name]["executions"] += 1
                agents[agent_name]["total_duration"] += exec_["duration"]
                if exec_["success"]:
                    agents[agent_name]["successes"] += 1
            
            # Calculate averages for each agent
            for agent_name, stats in agents.items():
                stats["success_rate"] = (stats["successes"] / stats["executions"]) * 100
                stats["avg_duration"] = stats["total_duration"] / stats["executions"]
            
            return {
                "total_executions": total_executions,
                "success_rate": success_rate,
                "avg_duration": avg_duration,
                "agents": dict(agents),
                "window_minutes": window_minutes
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system performance statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "disk_total": disk.total,
                "timestamp": time.time(),
                "datetime": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {
                "error": str(e),
                "timestamp": time.time(),
                "datetime": datetime.utcnow().isoformat()
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return {
            "request_stats": self.get_request_stats(),
            "agent_stats": self.get_agent_stats(),
            "system_stats": self.get_system_stats(),
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "total_agent_executions": self.total_agent_executions,
            "timestamp": time.time(),
            "datetime": datetime.utcnow().isoformat()
        }
    
    def _start_background_collection(self):
        """Start background system metrics collection"""
        def collect_system_metrics():
            while True:
                try:
                    system_stats = self.get_system_stats()
                    if "error" not in system_stats:
                        self.record_performance_metric("cpu_percent", system_stats["cpu_percent"])
                        self.record_performance_metric("memory_percent", system_stats["memory_percent"])
                        self.record_performance_metric("disk_percent", system_stats["disk_percent"])
                    
                    time.sleep(60)  # Collect every minute
                except Exception as e:
                    logger.error(f"Background metrics collection failed: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()


class LogCollector:
    """Collects and manages application logs"""
    
    def __init__(self, max_logs: int = 10000):
        self.max_logs = max_logs
        self.logs = deque(maxlen=max_logs)
        self.lock = threading.Lock()
    
    def add_log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Add a log entry"""
        log_entry = {
            "timestamp": time.time(),
            "datetime": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "context": context or {}
        }
        
        with self.lock:
            self.logs.append(log_entry)
    
    def get_logs(self, level: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs, optionally filtered by level"""
        with self.lock:
            if level:
                filtered_logs = [log for log in self.logs if log["level"] == level]
            else:
                filtered_logs = list(self.logs)
            
            return filtered_logs[-limit:]
    
    def get_error_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent error logs"""
        return self.get_logs(level="ERROR", limit=limit)


class PerformanceMonitor:
    """Monitors application performance"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.log_collector = LogCollector()
        self.start_time = time.time()
    
    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Record a request"""
        self.metrics_collector.record_request(method, path, status_code, duration)
    
    def record_agent_execution(self, agent_name: str, duration: float, success: bool, 
                              confidence: Optional[float] = None, error: Optional[str] = None):
        """Record an agent execution"""
        self.metrics_collector.record_agent_execution(agent_name, duration, success, confidence, error)
    
    def log_info(self, component: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log an info message"""
        self.log_collector.add_log("INFO", f"[{component}] {message}", context)
        logger.info(f"[{component}] {message}")
    
    def log_warning(self, component: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a warning message"""
        self.log_collector.add_log("WARNING", f"[{component}] {message}", context)
        logger.warning(f"[{component}] {message}")
    
    def log_error(self, component: str, message: str, error: Optional[str] = None, 
                  context: Optional[Dict[str, Any]] = None):
        """Log an error message"""
        full_message = f"[{component}] {message}"
        if error:
            full_message += f" - Error: {error}"
        
        self.log_collector.add_log("ERROR", full_message, context)
        logger.error(full_message)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return self.metrics_collector.get_all_metrics()
    
    def get_logs(self, level: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs"""
        return self.log_collector.get_logs(level, limit)
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self.start_time


# Global monitoring instance
_monitor = None


def get_monitor() -> PerformanceMonitor:
    """Get the global monitoring instance"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor


def setup_monitoring() -> None:
    """Setup monitoring system"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
        logger.info("Monitoring system initialized")


def instrument_fastapi(app) -> None:
    """Instrument FastAPI application for monitoring"""
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class MonitoringMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            start_time = time.time()
            
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            monitor = get_monitor()
            monitor.record_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
    
    # Add monitoring middleware
    app.add_middleware(MonitoringMiddleware)
    logger.info("FastAPI application instrumented for monitoring")


def create_health_check() -> Dict[str, Any]:
    """Create a comprehensive health check response"""
    monitor = get_monitor()
    
    try:
        system_stats = monitor.get_metrics()["system_stats"]
        
        # Determine overall health
        health_status = "healthy"
        issues = []
        
        # Check CPU usage
        if system_stats.get("cpu_percent", 0) > 90:
            health_status = "degraded"
            issues.append("High CPU usage")
        
        # Check memory usage
        if system_stats.get("memory_percent", 0) > 90:
            health_status = "degraded"
            issues.append("High memory usage")
        
        # Check disk usage
        if system_stats.get("disk_percent", 0) > 90:
            health_status = "degraded"
            issues.append("High disk usage")
        
        # Check error rate
        request_stats = monitor.get_metrics()["request_stats"]
        if request_stats.get("error_rate", 0) > 10:
            health_status = "degraded"
            issues.append("High error rate")
        
        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": monitor.get_uptime(),
            "system_stats": system_stats,
            "request_stats": request_stats,
            "issues": issues
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


def export_metrics_prometheus() -> str:
    """Export metrics in Prometheus format"""
    monitor = get_monitor()
    metrics = monitor.get_metrics()
    
    prometheus_metrics = []
    
    # System metrics
    system_stats = metrics.get("system_stats", {})
    if "cpu_percent" in system_stats:
        prometheus_metrics.append(f"system_cpu_percent {system_stats['cpu_percent']}")
    if "memory_percent" in system_stats:
        prometheus_metrics.append(f"system_memory_percent {system_stats['memory_percent']}")
    if "disk_percent" in system_stats:
        prometheus_metrics.append(f"system_disk_percent {system_stats['disk_percent']}")
    
    # Request metrics
    request_stats = metrics.get("request_stats", {})
    prometheus_metrics.append(f"http_requests_total {request_stats.get('total_requests', 0)}")
    prometheus_metrics.append(f"http_request_duration_seconds {request_stats.get('avg_response_time', 0)}")
    prometheus_metrics.append(f"http_errors_total {request_stats.get('total_requests', 0) * request_stats.get('error_rate', 0) / 100}")
    
    # Agent metrics
    agent_stats = metrics.get("agent_stats", {})
    prometheus_metrics.append(f"agent_executions_total {agent_stats.get('total_executions', 0)}")
    prometheus_metrics.append(f"agent_success_rate {agent_stats.get('success_rate', 0)}")
    
    return "\n".join(prometheus_metrics)