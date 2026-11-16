import psutil
import platform
import datetime
import time
import socket

def get_system_metrics():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "uptime": round((time.time() - psutil.boot_time()) / 3600, 2),
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "platform": platform.platform(),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.platform(),
        "processor": platform.processor(),
        "cpu_cores": psutil.cpu_count(),
        "total_ram": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_total": round(psutil.disk_usage("/").total / (1024**3), 2)
    }
