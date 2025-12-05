from typing import List, Callable
from hashfi.sensors.base import BaseSensor


class ThreatMonitor:
    def __init__(self, threshold: float = 0.9):
        self.sensors: List[BaseSensor] = []
        self.threshold = threshold
        self.current_threat_level = 0.0
        self.on_threshold_breach: Callable[[], None] = lambda: None

    def add_sensor(self, sensor: BaseSensor):
        self.sensors.append(sensor)

    def check_threats(self) -> float:
        """
        Polls all sensors and calculates the weighted average threat level.
        Returns the aggregate threat level (0.0 - 1.0).
        """
        if not self.sensors:
            return 0.0

        total_score = 0.0
        total_weight = 0.0

        for sensor in self.sensors:
            score = sensor.check_threat()
            total_score += score * sensor.weight
            total_weight += sensor.weight

        if total_weight == 0:
            self.current_threat_level = 0.0
        else:
            self.current_threat_level = total_score / total_weight

        # Check threshold
        if self.current_threat_level >= self.threshold:
            self.on_threshold_breach()

        return self.current_threat_level
