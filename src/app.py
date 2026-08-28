import platform
import logging
import keyboard
import mouse
import pystray
from PIL import Image

from src.config import get_data_dir, get_asset_dir, load_config, save_config
from src.setup_ui import prompt_initial_binding, SettingsDialog
from src.manager import WifiToggleManager
from src.controllers.windows import WindowsWifi
from src.controllers.macos import MacOSWifi
from src.controllers.linux import LinuxWifi


class WifiTogglerApp:
    def __init__(self):
        self.data_dir = get_data_dir()
        self.asset_dir = get_asset_dir()
        self.config_path = self.data_dir / "config.json"

        self.logger = self._setup_logger()
        self.config = self._initialize_config()

        controller = self._get_controller()
        self.manager = WifiToggleManager(controller, self.config.get("delay_seconds", 16.0))
        self.settings_open = False

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("WifiToggler")
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        file_handler = logging.FileHandler(self.data_dir / "app.log", encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def _initialize_config(self) -> dict:
        if not self.config_path.exists():
            self.logger.info("Config missing. Prompting initial setup.")
            config_data = prompt_initial_binding(self.asset_dir)
            save_config(self.config_path, config_data)
            return config_data
        return load_config(self.config_path)

    def _get_controller(self):
        os_name = platform.system()
        if os_name == "Windows": return WindowsWifi()
        if os_name == "Darwin": return MacOSWifi()
        if os_name == "Linux": return LinuxWifi()
        raise NotImplementedError(f"OS {os_name} is not supported.")

    def _setup_hooks(self):
        hotkey = self.config.get("hotkey", "f6")
        mouse_buttons = {"left", "right", "middle", "x", "x2"}

        if hotkey in mouse_buttons:
            mouse.on_button(self.manager.toggle, buttons=(hotkey,), types=('down',))
        else:
            keyboard.on_press_key(hotkey, lambda _: self.manager.toggle())

    def _open_settings(self, icon, item):
        if getattr(self, 'settings_open', False):
            return

        self.settings_open = True

        try:
            try:
                keyboard.unhook_all()
                mouse.unhook_all()
            except Exception as e:
                self.logger.warning(f"Failed to unhook: {e}")

            dialog = SettingsDialog(self.config, self.asset_dir)
            result = dialog.show()

            if result:
                self.config = result
                save_config(self.config_path, self.config)
                self.manager.delay = self.config.get("delay_seconds", 16.0)
        except Exception as e:
            self.logger.error(f"Error in settings dialog: {e}")
        finally:
            self._setup_hooks()
            self.settings_open = False

    def run(self):
        self._setup_hooks()

        icon_path = self.asset_dir / "icon.ico"
        tray_image = Image.open(icon_path) if icon_path.exists() else Image.new('RGB', (64, 64), color=(0, 0, 0))

        def on_quit(icon, item):
            self.manager.cleanup()
            icon.stop()

        tray_menu = pystray.Menu(
            pystray.MenuItem("Settings", self._open_settings, default=True),
            pystray.MenuItem("Quit", on_quit)
        )
        tray_icon = pystray.Icon("WifiToggler", tray_image, "Wi-Fi Toggler", menu=tray_menu)

        tray_icon.run()