import threading
import logging
from src.controllers.base import WifiController

logger = logging.getLogger("WifiToggler.Manager")


class WifiToggleManager:
    """
    Manages the Wi-Fi toggle logic, including state tracking
    and the auto-enable timer functionality.
    """

    def __init__(self, controller: WifiController, delay_seconds: float = 16.0):
        self.controller = controller
        self.delay = delay_seconds
        self.wifi_is_on = self.controller.is_enabled()
        self.timer = None
        self.lock = threading.Lock()

    def toggle(self) -> None:
        """Toggles the Wi-Fi state safely using a thread lock."""
        with self.lock:
            if self.wifi_is_on:
                self._disable()
            else:
                self._enable()

    def _enable(self) -> None:
        if self.timer:
            self.timer.cancel()
            self.timer = None

        logger.debug("Enabling Wi-Fi...")
        self.controller.turn_on()
        self.wifi_is_on = True
        logger.debug("Wi-Fi enabled.")

    def _disable(self) -> None:
        logger.debug("Disabling Wi-Fi...")
        self.controller.turn_off()
        self.wifi_is_on = False
        logger.debug(f"Wi-Fi disabled. Auto-enable timer set for {self.delay} seconds.")

        # failsafe for Roblox. the game kicks players after 20 seconds of no internet connection.
        # this timer ensures wi-fi is restored automatically before the server disconnects the client.
        self.timer = threading.Timer(self.delay, self._auto_enable)
        self.timer.start()

    def _auto_enable(self) -> None:
        with self.lock:
            if not self.wifi_is_on:
                logger.info("[AUTO] Timer expired. Auto-enabling Wi-Fi.")
                self._enable()

    def cleanup(self) -> None:
        """Cancels the active timer to allow clean application shutdown."""
        if self.timer:
            self.timer.cancel()