import logging
import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import psutil
import threading
from collections import defaultdict, deque

from .config import get_settings, get_agent_config, get_workflow_config

settings = get_settings()
agent_config = get_agent_config()
workflow_config = get_workflow_config()


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str]
    timestamp: datetime
    description: str = ""


@dataclass
class LogEntry:
    """Log entry data structure"""
    timestamp: datetime
    level: LogLevel
    message: str
    module: str
    function: str
    line_number: int
    extra_data: Dict[str, Any]
    trace_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class AgentExecutionMetrics:
    """Agent execution metrics"""
    agent_type: str
    execution_time: float
    confidence: float
    success: bool
    error_message: Optional[str] = None
    input_size: int
    output_size: int
    memory_usage: float
    cpu_usage: float


@dataclass
class WorkflowMetrics:
    """Workflow execution metrics"""
    workflow_id: str
    total_stages: int
    completed_stages: int
    failed_stages: int
    total_execution_time: float
    average_stage_time: float
    memory_peak: float
    cpu_peak: float
    status: str


class MetricsCollector:
    """Metrics collection and storage"""
    
    def __init__(self):
        self.metrics: List[Metric] = []
        self.metrics_lock = threading.Lock()
        self.max_metrics = 10000
        
    def add_metric(self, metric: Metric):
        """Add a metric to the collection"""
        with self.metrics_lock:
            self.metrics.append(metric)
            if len(self.metrics) > self.max_metrics:
                # Remove oldest metrics
                self.metrics = self.metrics[-self.max_metrics:]
    
    def get_metrics(self, metric_name: Optional[str] = None, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[Metric]:
        """Get metrics with optional filtering"""
        with self.metrics_lock:
            filtered_metrics = self.metrics
            
            if metric_name:
                filtered_metrics = [m for m in filtered_metrics if m.name == metric_name]
            
            if start_time:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
            
            if end_time:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
            
            return filtered_metrics
    
    def get_metric_summary(self, metric_name: str, 
                          time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window
        
        metrics = self.get_metrics(metric_name, start_time, end_time)
        
        if not metrics:
            return {
                "count": 0,
                "min": 0,
                "max": 0,
                "avg": 0,
                "sum": 0
            }
        
        values = [m.value for m in metrics]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values)
        }


class LogCollector:
    """Log collection and storage"""
    
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.logs_lock = threading.Lock()
        self.max_logs = 10000
        
    def add_log(self, log_entry: LogEntry):
        """Add a log entry to the collection"""
        with self.logs_lock:
            self.logs.append(log_entry)
            if len(self.logs) > self.max_logs:
                # Remove oldest logs
                self.logs = self.logs[-self.max_logs:]
    
    def get_logs(self, level: Optional[LogLevel] = None,
                module: Optional[str] = None,
                start_time: Optional[datetime] = None,
                end_time: Optional[datetime] = None,
                trace_id: Optional[str] = None) -> List[LogEntry]:
        """Get logs with optional filtering"""
        with self.logs_lock:
            filtered_logs = self.logs
            
            if level:
                filtered_logs = [l for l in filtered_logs if l.level == level]
            
            if module:
                filtered_logs = [l for l in filtered_logs if l.module == module]
            
            if start_time:
                filtered_logs = [l for l in filtered_logs if l.timestamp >= start_time]
            
            if end_time:
                filtered_logs = [l for l in filtered_logs if l.timestamp <= end_time]
            
            if trace_id:
                filtered_logs = [l for l in filtered_logs if l.trace_id == trace_id]
            
            return filtered_logs


class PerformanceMonitor:
    """System performance monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics_collector = MetricsCollector()
        self.log_collector = LogCollector()
        self.agent_metrics: Dict[str, List[AgentExecutionMetrics]] = defaultdict(list)
        self.workflow_metrics: Dict[str, WorkflowMetrics] = {}
        self.system_metrics = deque(maxlen=1000)
        
        # Start system monitoring
        if settings.ENABLE_MONITORING:
            self._start_system_monitoring()
    
    def _start_system_monitoring(self):
        """Start system monitoring thread"""
        def monitor_system():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.metrics_collector.add_metric(Metric(
                        name="system_cpu_usage",
                        value=cpu_percent,
                        metric_type=MetricType.GAUGE,
                        labels={"component": "system"},
                        timestamp=datetime.utcnow(),
                        description="System CPU usage percentage"
                    ))
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.metrics_collector.add_metric(Metric(
                        name="system_memory_usage",
                        value=memory.percent,
                        metric_type=MetricType.GAUGE,
                        labels={"component": "system"},
                        timestamp=datetime.utcnow(),
                        description="System memory usage percentage"
                    ))
                    
                    # Disk usage
                    disk = psutil.disk_usage('/')
                    self.metrics_collector.add_metric(Metric(
                        name="system_disk_usage",
                        value=(disk.used / disk.total) * 100,
                        metric_type=MetricType.GAUGE,
                        labels={"component": "system"},
                        timestamp=datetime.utcnow(),
                        description="System disk usage percentage"
                    ))
                    
                    # Store system metrics
                    self.system_metrics.append({
                        "timestamp": datetime.utcnow(),
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "disk_percent": (disk.used / disk.total) * 100
                    })
                    
                    time.sleep(workflow_config.MONITORING_INTERVAL)
                    
                except Exception as e:
                    self.log_error("system_monitor", "Failed to collect system metrics", str(e))
                    time.sleep(5)
        
        thread = threading.Thread(target=monitor_system, daemon=True)
        thread.start()
    
    def log_info(self, module: str, message: str, extra_data: Dict[str, Any] = None,
                trace_id: Optional[str] = None, user_id: Optional[str] = None):
        """Log info message"""
        self._log(LogLevel.INFO, module, message, extra_data or {}, trace_id, user_id)
    
    def log_warning(self, module: str, message: str, extra_data: Dict[str, Any] = None,
                   trace_id: Optional[str] = None, user_id: Optional[str] = None):
        """Log warning message"""
        self._log(LogLevel.WARNING, module, message, extra_data or {}, trace_id, user_id)
    
    def log_error(self, module: str, message: str, error_details: str = None,
                 trace_id: Optional[str] = None, user_id: Optional[str] = None):
        """Log error message"""
        extra_data = {"error_details": error_details} if error_details else {}
        self._log(LogLevel.ERROR, module, message, extra_data, trace_id, user_id)
    
    def log_critical(self, module: str, message: str, error_details: str = None,
                    trace_id: Optional[str] = None, user_id: Optional[str] = None):
        """Log critical message"""
        extra_data = {"error_details": error_details} if error_details else {}
        self._log(LogLevel.CRITICAL, module, message, extra_data, trace_id, user_id)
    
    def _log(self, level: LogLevel, module: str, message: str, extra_data: Dict[str, Any],
             trace_id: Optional[str] = None, user_id: Optional[str] = None):
        """Internal logging method"""
        # Get caller information
        frame = traceback.extract_stack()[-2]
        
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            module=module,
            function=frame.name,
            line_number=frame.lineno,
            extra_data=extra_data,
            trace_id=trace_id,
            user_id=user_id
        )
        
        self.log_collector.add_log(log_entry)
        
        # Also log to standard logging
        logger = logging.getLogger(module)
        log_message = f"{message} | {json.dumps(extra_data)}" if extra_data else message
        getattr(logger, level.value.lower())(log_message)
    
    @contextmanager
    def monitor_agent_execution(self, agent_type: str, trace_id: Optional[str] = None):
        """Context manager for monitoring agent execution"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.Process().cpu_percent()
        
        try:
            yield
            success = True
            error_message = None
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            end_cpu = psutil.Process().cpu_percent()
            
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = end_cpu - start_cpu
            
            # Record agent metrics
            agent_metric = AgentExecutionMetrics(
                agent_type=agent_type,
                execution_time=execution_time,
                confidence=0.0,  # Will be set by agent
                success=success,
                error_message=error_message,
                input_size=0,  # Will be set by agent
                output_size=0,  # Will be set by agent
                memory_usage=memory_usage,
                cpu_usage=cpu_usage
            )
            
            self.agent_metrics[agent_type].append(agent_metric)
            
            # Add metrics
            self.metrics_collector.add_metric(Metric(
                name="agent_execution_time",
                value=execution_time,
                metric_type=MetricType.HISTOGRAM,
                labels={"agent_type": agent_type, "success": str(success)},
                timestamp=datetime.utcnow(),
                description=f"Execution time for {agent_type} agent"
            ))
            
            self.metrics_collector.add_metric(Metric(
                name="agent_memory_usage",
                value=memory_usage,
                metric_type=MetricType.HISTOGRAM,
                labels={"agent_type": agent_type},
                timestamp=datetime.utcnow(),
                description=f"Memory usage for {agent_type} agent"
            ))
            
            # Log execution
            if success:
                self.log_info(
                    "agent_execution",
                    f"Agent {agent_type} executed successfully",
                    {
                        "execution_time": execution_time,
                        "memory_usage": memory_usage,
                        "cpu_usage": cpu_usage
                    },
                    trace_id
                )
            else:
                self.log_error(
                    "agent_execution",
                    f"Agent {agent_type} execution failed",
                    error_message,
                    trace_id
                )
    
    @asynccontextmanager
    async def monitor_workflow_execution(self, workflow_id: str, total_stages: int,
                                       trace_id: Optional[str] = None):
        """Context manager for monitoring workflow execution"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.Process().cpu_percent()
        
        workflow_metric = WorkflowMetrics(
            workflow_id=workflow_id,
            total_stages=total_stages,
            completed_stages=0,
            failed_stages=0,
            total_execution_time=0.0,
            average_stage_time=0.0,
            memory_peak=start_memory,
            cpu_peak=start_cpu,
            status="running"
        )
        
        self.workflow_metrics[workflow_id] = workflow_metric
        
        try:
            yield workflow_metric
            workflow_metric.status = "completed"
        except Exception as e:
            workflow_metric.status = "failed"
            raise
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            end_cpu = psutil.Process().cpu_percent()
            
            workflow_metric.total_execution_time = end_time - start_time
            workflow_metric.memory_peak = max(workflow_metric.memory_peak, end_memory)
            workflow_metric.cpu_peak = max(workflow_metric.cpu_peak, end_cpu)
            
            if workflow_metric.completed_stages > 0:
                workflow_metric.average_stage_time = workflow_metric.total_execution_time / workflow_metric.completed_stages
            
            # Add workflow metrics
            self.metrics_collector.add_metric(Metric(
                name="workflow_execution_time",
                value=workflow_metric.total_execution_time,
                metric_type=MetricType.HISTOGRAM,
                labels={"workflow_id": workflow_id, "status": workflow_metric.status},
                timestamp=datetime.utcnow(),
                description=f"Execution time for workflow {workflow_id}"
            ))
            
            self.metrics_collector.add_metric(Metric(
                name="workflow_stages_completed",
                value=workflow_metric.completed_stages,
                metric_type=MetricType.COUNTER,
                labels={"workflow_id": workflow_id},
                timestamp=datetime.utcnow(),
                description=f"Completed stages for workflow {workflow_id}"
            ))
            
            # Log workflow completion
            self.log_info(
                "workflow_execution",
                f"Workflow {workflow_id} {workflow_metric.status}",
                {
                    "total_stages": total_stages,
                    "completed_stages": workflow_metric.completed_stages,
                    "failed_stages": workflow_metric.failed_stages,
                    "total_execution_time": workflow_metric.total_execution_time,
                    "memory_peak": workflow_metric.memory_peak,
                    "cpu_peak": workflow_metric.cpu_peak
                },
                trace_id
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        if not self.system_metrics:
            return {
                "status": "unknown",
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
                "uptime": time.time() - self.start_time
            }
        
        latest = self.system_metrics[-1]
        return {
            "status": "healthy" if latest["cpu_percent"] < 80 and latest["memory_percent"] < 80 else "warning",
            "cpu_usage": latest["cpu_percent"],
            "memory_usage": latest["memory_percent"],
            "disk_usage": latest["disk_percent"],
            "uptime": time.time() - self.start_time
        }
    
    def get_agent_performance_summary(self, agent_type: Optional[str] = None,
                                    time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Get agent performance summary"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window
        
        if agent_type:
            metrics = [m for m in self.agent_metrics[agent_type] 
                      if m.execution_time >= start_time.timestamp()]
        else:
            all_metrics = []
            for agent_metrics in self.agent_metrics.values():
                all_metrics.extend([m for m in agent_metrics 
                                  if m.execution_time >= start_time.timestamp()])
            metrics = all_metrics
        
        if not metrics:
            return {
                "total_executions": 0,
                "success_rate": 0,
                "average_execution_time": 0,
                "average_memory_usage": 0,
                "average_cpu_usage": 0
            }
        
        total_executions = len(metrics)
        successful_executions = len([m for m in metrics if m.success])
        success_rate = successful_executions / total_executions if total_executions > 0 else 0
        
        return {
            "total_executions": total_executions,
            "success_rate": success_rate,
            "average_execution_time": sum(m.execution_time for m in metrics) / total_executions,
            "average_memory_usage": sum(m.memory_usage for m in metrics) / total_executions,
            "average_cpu_usage": sum(m.cpu_usage for m in metrics) / total_executions
        }
    
    def get_workflow_performance_summary(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Get workflow performance summary"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window
        
        workflows = [w for w in self.workflow_metrics.values() 
                    if w.total_execution_time >= start_time.timestamp()]
        
        if not workflows:
            return {
                "total_workflows": 0,
                "completed_workflows": 0,
                "failed_workflows": 0,
                "average_execution_time": 0,
                "average_stages_completed": 0
            }
        
        total_workflows = len(workflows)
        completed_workflows = len([w for w in workflows if w.status == "completed"])
        failed_workflows = len([w for w in workflows if w.status == "failed"])
        
        return {
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "failed_workflows": failed_workflows,
            "average_execution_time": sum(w.total_execution_time for w in workflows) / total_workflows,
            "average_stages_completed": sum(w.completed_stages for w in workflows) / total_workflows
        }
    
    def get_metrics_summary(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        return {
            "system": self.get_system_status(),
            "agents": self.get_agent_performance_summary(time_window=time_window),
            "workflows": self.get_workflow_performance_summary(time_window=time_window),
            "metrics_count": len(self.metrics_collector.metrics),
            "logs_count": len(self.log_collector.logs)
        }


# Global monitoring instance
monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get the global monitoring instance"""
    return monitor


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    
    monitor.log_info("monitoring", "Logging system initialized")


def log_agent_execution(agent_type: str, execution_time: float, confidence: float,
                       success: bool, input_size: int, output_size: int,
                       error_message: Optional[str] = None, trace_id: Optional[str] = None):
    """Log agent execution metrics"""
    if monitor.agent_metrics[agent_type]:
        # Update the latest agent metric with additional data
        latest_metric = monitor.agent_metrics[agent_type][-1]
        latest_metric.confidence = confidence
        latest_metric.input_size = input_size
        latest_metric.output_size = output_size
        
        # Add confidence metric
        monitor.metrics_collector.add_metric(Metric(
            name="agent_confidence",
            value=confidence,
            metric_type=MetricType.GAUGE,
            labels={"agent_type": agent_type, "success": str(success)},
            timestamp=datetime.utcnow(),
            description=f"Confidence score for {agent_type} agent"
        ))
        
        # Add throughput metric
        if execution_time > 0:
            throughput = output_size / execution_time
            monitor.metrics_collector.add_metric(Metric(
                name="agent_throughput",
                value=throughput,
                metric_type=MetricType.GAUGE,
                labels={"agent_type": agent_type},
                timestamp=datetime.utcnow(),
                description=f"Throughput for {agent_type} agent (output_size/time)"
            ))


def log_workflow_stage_completion(workflow_id: str, stage_name: str, success: bool,
                                execution_time: float, trace_id: Optional[str] = None):
    """Log workflow stage completion"""
    if workflow_id in monitor.workflow_metrics:
        workflow = monitor.workflow_metrics[workflow_id]
        
        if success:
            workflow.completed_stages += 1
        else:
            workflow.failed_stages += 1
        
        # Add stage completion metric
        monitor.metrics_collector.add_metric(Metric(
            name="workflow_stage_completion",
            value=1 if success else 0,
            metric_type=MetricType.COUNTER,
            labels={"workflow_id": workflow_id, "stage_name": stage_name, "success": str(success)},
            timestamp=datetime.utcnow(),
            description=f"Stage completion for {stage_name} in workflow {workflow_id}"
        ))
        
        monitor.log_info(
            "workflow_stage",
            f"Workflow {workflow_id} stage {stage_name} {'completed' if success else 'failed'}",
            {
                "execution_time": execution_time,
                "completed_stages": workflow.completed_stages,
                "failed_stages": workflow.failed_stages
            },
            trace_id
        )


def setup_monitoring():
    """Setup monitoring and observability"""
    try:
        # Setup logging
        setup_logging()
        
        # Initialize monitoring
        monitor.log_info("monitoring", "Monitoring system initialized")
        
        # Setup Prometheus metrics endpoint if enabled
        if settings.ENABLE_MONITORING:
            monitor.log_info("monitoring", "Metrics collection enabled")
        
        print("✅ Monitoring setup complete")
        
    except Exception as e:
        print(f"⚠️ Monitoring setup failed: {e}")


def instrument_fastapi(app):
    """Instrument FastAPI application with monitoring"""
    try:
        from fastapi import Request, Response
        import time
        
        @app.middleware("http")
        async def monitoring_middleware(request: Request, call_next):
            start_time = time.time()
            
            # Process request
            response = await call_next(request)
            
            # Calculate metrics
            process_time = time.time() - start_time
            
            # Record API metrics
            monitor.metrics_collector.add_metric(Metric(
                name="http_request_duration",
                value=process_time,
                metric_type=MetricType.HISTOGRAM,
                labels={
                    "method": request.method,
                    "endpoint": str(request.url.path),
                    "status_code": str(response.status_code)
                },
                timestamp=datetime.utcnow(),
                description="HTTP request duration"
            ))
            
            monitor.metrics_collector.add_metric(Metric(
                name="http_requests_total",
                value=1,
                metric_type=MetricType.COUNTER,
                labels={
                    "method": request.method,
                    "endpoint": str(request.url.path),
                    "status_code": str(response.status_code)
                },
                timestamp=datetime.utcnow(),
                description="Total HTTP requests"
            ))
            
            # Add response time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        
        monitor.log_info("monitoring", "FastAPI instrumentation complete")
        
    except Exception as e:
        monitor.log_error("monitoring", "FastAPI instrumentation failed", str(e))