import psutil
import random
from hashfi.sensors.base import BaseSensor


class SystemSensor(BaseSensor):
    def __init__(self):
        super().__init__(name="System Telemetry", weight=1.0)

    def check_threat(self) -> float:
        threat = 0.0

        # 1. CPU Usage Check
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > 80:
            threat += 0.4
        elif cpu_percent > 50:
            threat += 0.2

        # 2. Network Connections Check
        # Count established connections
        try:
            connections = len(psutil.net_connections(kind="inet"))
            if connections > 100:
                threat += 0.3
            elif connections > 50:
                threat += 0.1
        except Exception:
            pass  # Permission denied or other error

        # 3. Random Jitter (to simulate fluctuating threat levels for the demo)
        # In a real app, this would be specific heuristic checks
        threat += random.uniform(0.0, 0.2)

        # Cap at 1.0
        return min(threat, 1.0)
