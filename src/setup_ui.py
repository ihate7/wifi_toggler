import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import mouse
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("WifiToggler.SetupUI")


class SettingsDialog:
    def __init__(self, current_config: Dict[str, Any], asset_dir: Path):
        self.initial_config = current_config
        self.asset_dir = asset_dir
        self.result: Optional[Dict[str, Any]] = None

        self.current_hotkey = self.initial_config.get("hotkey", "f6")
        self.is_listening = False

        self._init_window()
        self._build_ui()
        self._setup_hooks()

    def _init_window(self) -> None:
        self.root = tk.Tk()
        self.root.title("Settings")
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)

        self.style = ttk.Style()
        if 'vista' in self.style.theme_names():
            self.style.theme_use('vista')

        self.root.configure(bg="#F0F0F0")
        self.root.option_add("*Font", ("Segoe UI", 9))

        icon_path = self.asset_dir / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(icon_path)

    def _build_ui(self) -> None:
        self.frame = ttk.Frame(self.root, padding="15 15 15 15")
        self.frame.pack(expand=True, fill=tk.BOTH)

        # Row 0: Hotkey
        ttk.Label(self.frame, text="Toggle Hotkey:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10), padx=(0, 20)
        )

        self.hotkey_entry = ttk.Entry(self.frame, width=25, justify=tk.LEFT)
        self.hotkey_entry.insert(0, self.current_hotkey.upper())
        self.hotkey_entry.bind("<Key>", lambda e: "break")
        self.hotkey_entry.bind("<FocusIn>", self._on_focus_in)
        self.hotkey_entry.bind("<FocusOut>", self._on_focus_out)
        self.hotkey_entry.grid(row=0, column=1, sticky=tk.E, pady=(0, 10))

        # Row 1: Delay
        ttk.Label(self.frame, text="Hotkey Delay (Seconds):").grid(
            row=1, column=0, sticky=tk.W, pady=(0, 15), padx=(0, 20)
        )

        self.delay_var = tk.StringVar(value=str(self.initial_config.get("delay_seconds", 16.0)))
        self.delay_entry = ttk.Entry(self.frame, textvariable=self.delay_var, width=25, justify=tk.LEFT)
        self.delay_entry.grid(row=1, column=1, sticky=tk.E, pady=(0, 15))

        # Row 2: Buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=tk.E)

        ok_btn = ttk.Button(btn_frame, text="OK", width=10, command=self._on_ok)
        ok_btn.pack(side=tk.LEFT, padx=(0, 5))

        cancel_btn = ttk.Button(btn_frame, text="Cancel", width=10, command=self._on_cancel)
        cancel_btn.pack(side=tk.LEFT)

        self.root.update_idletasks()
        self.root.eval('tk::PlaceWindow . center')
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _setup_hooks(self) -> None:
        mouse.hook(self._on_mouse)
        keyboard.hook(self._on_key)

    def _teardown_hooks(self) -> None:
        try:
            mouse.unhook(self._on_mouse)
            keyboard.unhook(self._on_key)
        except (KeyError, ValueError):
            pass

    def _update_hotkey_ui(self, key_name: str) -> None:
        self.current_hotkey = key_name
        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_entry.insert(0, self.current_hotkey.upper())
        self.root.focus()

    def _on_focus_in(self, event) -> None:
        self.is_listening = True
        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_entry.insert(0, "Press any key...")

    def _on_focus_out(self, event) -> None:
        if self.is_listening:
            self.is_listening = False
            self._update_hotkey_ui(self.current_hotkey)

    def _on_mouse(self, event) -> None:
        if not self.is_listening:
            return

        if isinstance(event, mouse.ButtonEvent) and event.event_type in ('down', 'double'):
            if event.button == 'left':
                return

            self.is_listening = False
            self.root.after(0, lambda: self._update_hotkey_ui(event.button))

    def _on_key(self, event) -> None:
        if not self.is_listening:
            return

        if event.event_type == 'down':
            if event.name in ['ctrl', 'shift', 'alt', 'windows', 'menu']:
                return

            self.is_listening = False
            self.root.after(0, lambda: self._update_hotkey_ui(event.name.lower()))

    def _on_ok(self) -> None:
        try:
            delay = float(self.delay_var.get())
            if delay < 0:
                raise ValueError

            self.result = {
                "hotkey": self.current_hotkey,
                "delay_seconds": delay
            }
            self._close()
        except ValueError:
            messagebox.showerror("Error", "Delay must be a positive number.", parent=self.root)

    def _on_cancel(self) -> None:
        self.result = None
        self._close()

    def _close(self) -> None:
        self._teardown_hooks()
        self.root.destroy()

    def show(self) -> Optional[Dict[str, Any]]:
        self.root.mainloop()
        return self.result


def prompt_initial_binding(asset_dir: Path) -> dict:
    default_config = {"hotkey": "f6", "delay_seconds": 16.0}
    dialog = SettingsDialog(default_config, asset_dir)
    result = dialog.show()
    return result if result else default_config