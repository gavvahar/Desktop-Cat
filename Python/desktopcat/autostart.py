"""Phase 8: enable/disable launching Desktop-Cat automatically at login.
Linux: an XDG autostart .desktop file. macOS: a LaunchAgent plist.
Windows: the per-user Run registry key. Plain functions -- no classes.

The macOS path is unverified -- there's no Mac available to test this on
(unlike Windows, which was verified via WSL interop). It's written to spec
(a standard per-user LaunchAgent) but treat it as best-effort until someone
confirms it on real hardware.
"""

import os, platform, sys

AUTOSTART_NAME = "desktopcat"


def _linux_autostart_path():
    return os.path.join(os.path.expanduser("~"), ".config", "autostart", "desktopcat.desktop")


def _macos_autostart_path():
    return os.path.join(os.path.expanduser("~"), "Library", "LaunchAgents", "com.desktopcat.plist")


def is_enabled():
    system = platform.system()
    if system == "Windows":
        return _windows_autostart_enabled()
    if system == "Darwin":
        return os.path.isfile(_macos_autostart_path())
    return os.path.isfile(_linux_autostart_path())


def set_enabled(enabled):
    system = platform.system()
    if system == "Windows":
        _set_windows_autostart(enabled)
    elif system == "Darwin":
        _set_macos_autostart(enabled)
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


def _set_macos_autostart(enabled):
    path = _macos_autostart_path()
    if not enabled:
        if os.path.isfile(path):
            os.remove(path)
        return

    os.makedirs(os.path.dirname(path), exist_ok=True)
    import plistlib

    plist = {
        "Label": "com.desktopcat",
        "ProgramArguments": [sys.executable, "-m", "desktopcat.main"],
        "RunAtLoad": True,
    }
    with open(path, "wb") as fh:
        plistlib.dump(plist, fh)


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
