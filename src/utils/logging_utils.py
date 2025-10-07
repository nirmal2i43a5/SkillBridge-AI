import logging
from typing import Optional

_DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

def setup_logging(level: int = logging.INFO, fmt: Optional[str] = None) -> None:
    """Configure root logger if it has not been configured yet."""
    if logging.getLogger().handlers:
        return
    logging.basicConfig(level=level, format=fmt or _DEFAULT_FORMAT)
