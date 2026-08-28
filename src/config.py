import sys
import json
import logging
from pathlib import Path


def get_data_dir() -> Path:
    """Returns the directory where the executable or script is located (for logs/configs)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def get_asset_dir() -> Path:
    """Returns the directory where bundled assets (like icon.ico) are extracted."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def load_config(config_path: Path) -> dict:
    default_config = {"hotkey": "f6", "delay_seconds": 16.0}

    if not config_path.exists():
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logging.getLogger("WifiToggler").error(f"Config load error: {e}")
        return default_config


def save_config(config_path: Path, data: dict) -> None:
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        logging.getLogger("WifiToggler").error(f"Config save error: {e}")