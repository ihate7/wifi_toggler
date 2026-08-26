import subprocess
from .base import WifiController


class LinuxWifi(WifiController):
    """
    Linux-specific Wi-Fi controller utilizing NetworkManager (nmcli).
    """

    def turn_on(self) -> None:
        subprocess.run(['nmcli', 'radio', 'wifi', 'on'])

    def turn_off(self) -> None:
        subprocess.run(['nmcli', 'radio', 'wifi', 'off'])

    def is_enabled(self) -> bool:
        result = subprocess.run(
            ['nmcli', '-t', '-f', 'WIFI', 'radio'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == 'enabled'