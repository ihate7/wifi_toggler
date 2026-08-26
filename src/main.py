import platform
import keyboard
import logging
import sys
import json
import threading
from pathlib import Path

from src.controllers.windows import WindowsWifi
from src.controllers.macos import MacOSWifi
from src.controllers.linux import LinuxWifi
from src.manager import WifiToggleManager


def get_app_dir() -> Path:
    """
    Determines the application directory.
    Handles both standard Python execution and PyInstaller frozen environments.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def load_config(app_dir: Path) -> dict:
    """
    Loads the configuration from config.json.
    Creates a default configuration file if it does not exist.
    """
    config_path = app_dir / "config.json"
    default_config = {
        "hotkey": "f6",
        "delay_seconds": 16.0
    }

    if not config_path.exists():
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)
        except IOError as e:
            logging.error(f"Failed to create default config: {e}")
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Failed to load config, using defaults. Error: {e}")
        return default_config


def setup_logger(app_dir: Path) -> logging.Logger:
    """
    Configures application logging.
    Logs to a file in the application directory and to stdout if not compiled.
    """
    logger = logging.getLogger("WifiToggler")
    logger.setLevel(logging.DEBUG)

    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    log_file_path = app_dir / "app.log"

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)

    if not getattr(sys, 'frozen', False):
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


def get_wifi_controller(logger: logging.Logger):
    """Instantiates the appropriate Wi-Fi controller based on the OS."""
    os_name = platform.system()
    logger.debug(f"Detecting OS: {os_name}")

    if os_name == "Windows":
        return WindowsWifi()
    elif os_name == "Darwin":
        return MacOSWifi()
    elif os_name == "Linux":
        return LinuxWifi()

    raise NotImplementedError(f"OS {os_name} is not supported.")


def main():
    app_dir = get_app_dir()
    logger = setup_logger(app_dir)
    config = load_config(app_dir)

    try:
        controller = get_wifi_controller(logger)
    except NotImplementedError as e:
        logger.error(str(e))
        return

    hotkey = config.get("hotkey", "f6")
    delay = config.get("delay_seconds", 16.0)

    manager = WifiToggleManager(controller=controller, delay_seconds=delay)

    logger.info(f"[{platform.system()}] Service started.")
    logger.info(f"Initial Wi-Fi state: {'ON' if manager.wifi_is_on else 'OFF'}")
    logger.info(f"Listening for hotkey: '{hotkey}'")

    keyboard.on_press_key(hotkey, lambda _: manager.toggle())

    # Keep the main thread alive indefinitely
    threading.Event().wait()


if __name__ == "__main__":
    main()