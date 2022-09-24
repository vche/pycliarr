import logging
from typing import Optional


def setup_logging(level: int = logging.INFO, filename: Optional[str] = None) -> None:
    """Configure standard logging."""
    logging.basicConfig(
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s: %(message)s", level=level, filename=filename
    )


def size_to_str(size: Optional[float]) -> str:
    if size is None:
        return "-"
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if abs(size) < 1024.0:
            return f"{size:3.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}YB"
