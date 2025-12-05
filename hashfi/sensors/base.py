from abc import ABC, abstractmethod


class BaseSensor(ABC):
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight

    @abstractmethod
    def check_threat(self) -> float:
        """
        Returns a threat score between 0.0 and 1.0.
        0.0 = No threat
        1.0 = Maximum threat
        """
        pass
