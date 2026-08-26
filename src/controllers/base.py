from abc import ABC, abstractmethod


class WifiController(ABC):
    """
    Abstract base class for OS-specific Wi-Fi controllers.
    Defines the standard interface for hardware interaction.
    """

    @abstractmethod
    def turn_on(self) -> None:
        """Enables the Wi-Fi adapter/radio."""
        pass

    @abstractmethod
    def turn_off(self) -> None:
        """Disables the Wi-Fi adapter/radio."""
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """
        Checks the current state of the Wi-Fi adapter.

        Returns:
            bool: True if Wi-Fi is currently enabled, False otherwise.
        """
        pass