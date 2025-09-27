import os
from typing import Optional, Any


def getenv_bool(name: str, default: bool = False) -> bool:
    """Read an environment variable and coerce to boolean.

    Accepts: 1/0, true/false, yes/no (case-insensitive).
    """
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "y"}


def coalesce(*values: Any, default: Optional[Any] = None) -> Optional[Any]:
    """Return the first non-empty (non-None and non-"") value, else default."""
    for v in values:
        if v is not None and v != "":
            return v
    return default

