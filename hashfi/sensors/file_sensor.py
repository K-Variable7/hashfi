import os
from hashfi.sensors.base import BaseSensor


class FileIntegritySensor(BaseSensor):
    def __init__(self, target_dir: str):
        super().__init__(name="File Integrity Monitor", weight=2.0)
        self.target_dir = target_dir
        self.file_snapshot = {}
        self._take_snapshot()

    def _take_snapshot(self):
        """Records modification times of all files in target_dir."""
        self.file_snapshot = {}
        for root, _, files in os.walk(self.target_dir):
            if "__pycache__" in root or ".git" in root or ".venv" in root:
                continue
            for file in files:
                if file.endswith(".pyc"):
                    continue
                path = os.path.join(root, file)
                try:
                    self.file_snapshot[path] = os.path.getmtime(path)
                except OSError:
                    pass

    def check_threat(self) -> float:
        """Checks if any file has been modified since snapshot."""
        changes_detected = 0
        current_files = set()

        for root, _, files in os.walk(self.target_dir):
            if "__pycache__" in root or ".git" in root or ".venv" in root:
                continue
            for file in files:
                if file.endswith(".pyc"):
                    continue
                path = os.path.join(root, file)
                current_files.add(path)
                try:
                    mtime = os.path.getmtime(path)

                    # Check modification
                    if path in self.file_snapshot:
                        if self.file_snapshot[path] != mtime:
                            # File modified
                            changes_detected += 1
                    else:
                        # New file
                        changes_detected += 1
                except OSError:
                    pass

        # Check for deletions
        for path in self.file_snapshot:
            if path not in current_files:
                changes_detected += 1

        if changes_detected > 0:
            return 1.0  # MAX THREAT

        return 0.0
