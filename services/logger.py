from datetime import datetime


def log(message: str, level: str = "INFO"):
    """
    Simple console logger with timestamp.
    Extend with file logging or structured logging (e.g. loguru) as needed.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")
