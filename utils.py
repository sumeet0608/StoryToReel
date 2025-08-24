import os, logging
from pathlib import Path

logger = logging.getLogger("reels_bot")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def ensure_dir(path: Path):
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured directory: {path}")


def ensure_dirs(dirs: list[str]):
    """Ensure a list of directories exists."""
    for d in dirs:
        ensure_dir(Path(d))