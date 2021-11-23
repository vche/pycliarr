import logging
from typing import Optional


def setup_logging(level: int = logging.INFO, filename: Optional[str] = None) -> None:
    """Configure standard logging."""
    logging.basicConfig(
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s: %(message)s", level=level, filename=filename
    )
