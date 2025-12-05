import os
import random


def secure_shred(file_path, passes=3):
    """
    Overwrite the file with random data multiple times before deleting.
    Returns True if successful, False otherwise.
    """
    try:
        if not os.path.isfile(file_path):
            return False
        length = os.path.getsize(file_path)
        with open(file_path, "r+b") as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(length))
                f.flush()
                os.fsync(f.fileno())
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"Shred error: {e}")
        return False
