"""Phase 8: enable/disable launching Desktop-Cat automatically at login.
Linux: an XDG autostart .desktop file. Windows: the per-user Run registry
key. Plain functions -- no classes.
"""

import os, platform, sys

AUTOSTART_NAME = "desktopcat"


def _linux_autostart_path():
    return os.path.join(os.path.expanduser("~"), ".config", "autostart", "desktopcat.desktop")


def is_enabled():
    if platform.system() == "Windows":
        return _windows_autostart_enabled()
    return os.path.isfile(_linux_autostart_path())


def set_enabled(enabled):
    if platform.system() == "Windows":
        _set_windows_autostart(enabled)
    else:
        _set_linux_autostart(enabled)


def _set_linux_autostart(enabled):
    path = _linux_autostart_path()
    if not enabled:
        if os.path.isfile(path):
            os.remove(path)
        return

    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Prefer the AppImage's own path (set by the AppImage runtime) so autostart
    # keeps working after the source checkout moves or is deleted; fall back
    # to re-invoking this same Python interpreter otherwise.
    command = os.environ.get("APPIMAGE") or f"{sys.executable} -m desktopcat.main"
    with open(path, "w") as fh:
        fh.write(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Desktop Cat\n"
            f"Exec={command}\n"
            "X-GNOME-Autostart-enabled=true\n"
        )


def _windows_autostart_enabled():
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
            winreg.QueryValueEx(key, AUTOSTART_NAME)
        return True
    except Exception:
        return False


def _set_windows_autostart(enabled):
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS
        ) as key:
            if enabled:
                winreg.SetValueEx(key, AUTOSTART_NAME, 0, winreg.REG_SZ, sys.executable)
            else:
                try:
                    winreg.DeleteValue(key, AUTOSTART_NAME)
                except FileNotFoundError:
                    pass
    except Exception:
        pass
