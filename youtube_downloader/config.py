from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)

def load_config() -> dict:
    """Load configuration from ~/.yt_downloader.yaml if it exists.

    Returns:
        dict: Configuration dictionary or empty dict if file doesn't exist.
    """
    config_path = Path.home() / ".yt_downloader.yaml"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}")
    return {}
