# Wi-Fi Toggler

A lightweight, cross-platform background utility to toggle the system's Wi-Fi state using a global hotkey. It features an auto-reconnect timer to ensure the network is restored automatically, which is particularly useful for preventing server disconnects in latency-sensitive applications and online games.

## Features

- **Native API Integration:** Uses native OS interfaces (WinRT on Windows, `networksetup` on macOS, `nmcli` on Linux) for fast and reliable radio state switching.
- **Auto-Reconnect Timer:** Automatically re-enables Wi-Fi after a configurable delay.
- **Cross-Platform:** Fully supports Windows, macOS, and Linux.
- **Background Execution:** Runs silently in the background without a console window.
- **Portable Configuration:** Automatically generates its configuration and log files in the same directory as the executable.

## Prerequisites

- Python 3.9+
- OS-specific requirements:
  - **Windows:** Windows 10/11 (utilizes the WinRT API).
  - **macOS:** Utilizes the built-in `networksetup` utility.
  - **Linux:** Requires NetworkManager (`nmcli`).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/wifi_toggler.git
   cd wifi_toggler
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Upon the first launch, the application creates a `config.json` file in its root directory:

```json
{
    "hotkey": "f6",
    "delay_seconds": 16.0
}
```

- `hotkey`: The global key combination used to toggle the Wi-Fi state (e.g., `f6`, `ctrl+shift+w`).
- `delay_seconds`: Time in seconds before the Wi-Fi adapter is automatically re-enabled. 

## Usage

Run the main script via Python:

```bash
python src/main.py
```

The application will run silently in the background. Press the configured hotkey to toggle your Wi-Fi state. All status changes and errors are recorded in `app.log`.

## Building a Standalone Executable (Windows)

To use the tool without setting up a Python environment, you can compile it into a single executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name WifiToggler src/main.py
```

The compiled `WifiToggler.exe` will be located in the `dist/` folder. You can place this executable anywhere on your system (e.g., in your Startup folder). It will automatically generate `config.json` and `app.log` in its current directory.