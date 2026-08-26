import subprocess
import re
from .base import WifiController


class MacOSWifi(WifiController):
    """
    macOS-specific Wi-Fi controller utilizing the 'networksetup' utility.
    """

    def __init__(self):
        self.interface = self._get_interface()

    def _get_interface(self) -> str:
        """Retrieves the primary Wi-Fi hardware port (usually en0)."""
        try:
            res = subprocess.run(
                ['networksetup', '-listallhardwareports'],
                capture_output=True,
                text=True
            )
            match = re.search(r'Hardware Port: (?:Wi-Fi|AirPort)\nDevice: (\w+)', res.stdout)
            return match.group(1) if match else 'en0'
        except Exception:
            return 'en0'

    def turn_on(self) -> None:
        subprocess.run(['networksetup', '-setairportpower', self.interface, 'on'])

    def turn_off(self) -> None:
        subprocess.run(['networksetup', '-setairportpower', self.interface, 'off'])

    def is_enabled(self) -> bool:
        res = subprocess.run(
            ['networksetup', '-getairportpower', self.interface],
            capture_output=True,
            text=True
        )
        return 'On' in res.stdout