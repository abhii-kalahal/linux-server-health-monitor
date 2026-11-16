import re
import os
import subprocess
from datetime import datetime

LOG_FILES = [
    "/var/log/auth.log",
    "/var/log/secure"
]

PATTERNS = {
    "Failed Login": r"Failed password",
    "Authentication Failure": r"authentication failure",
    "Invalid User": r"Invalid user",
    "Successful Login": r"Accepted password|Accepted publickey"
}

def read_log_file():
    for path in LOG_FILES:
        if os.path.exists(path):
            try:
                with open(path, "r", errors="ignore") as file:
                    lines = file.readlines()
                    if lines:
                        return lines
            except PermissionError:
                continue

    try:
        result = subprocess.run(
            ["journalctl", "-u", "ssh", "--no-pager", "-n", "500"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.splitlines()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return []

def analyze_logs():
    lines = read_log_file()
    events = []

    for line in lines:
        for event_type, pattern in PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                events.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "event_type": event_type,
                    "details": line.strip()
                })
                break

    return events
