import asyncio
import logging
import winrt.windows.devices.radios as radios
from .base import WifiController

logger = logging.getLogger("WifiToggler.Windows")


class WindowsWifi(WifiController):
    """
    Windows-specific Wi-Fi controller utilizing the WinRT API
    for native, low-latency radio state management.
    """

    def __init__(self):
        self.wifi_radio = self._get_wifi_radio()
        if not self.wifi_radio:
            logger.error("Wi-Fi radio not found on this system.")

    def _get_wifi_radio(self):
        """Asynchronously retrieves the Wi-Fi radio device."""

        async def fetch():
            radio_list = await radios.Radio.get_radios_async()
            for r in radio_list:
                if r.kind == radios.RadioKind.WI_FI:
                    return r
            return None

        return asyncio.run(fetch())

    def turn_on(self) -> None:
        if self.wifi_radio:
            async def _turn_on():
                await self.wifi_radio.set_state_async(radios.RadioState.ON)

            asyncio.run(_turn_on())
            logger.debug("Wi-Fi radio turned ON via WinRT.")

    def turn_off(self) -> None:
        if self.wifi_radio:
            async def _turn_off():
                await self.wifi_radio.set_state_async(radios.RadioState.OFF)

            asyncio.run(_turn_off())
            logger.debug("Wi-Fi radio turned OFF via WinRT.")

    def is_enabled(self) -> bool:
        if self.wifi_radio:
            return self.wifi_radio.state == radios.RadioState.ON
        return False