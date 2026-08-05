import os, platform, sys

from PySide6.QtWidgets import QApplication

from desktopcat.window import CatWindow


def main():
    if platform.system() == "Linux":
        # Qt silently prefers the Wayland platform plugin whenever
        # WAYLAND_DISPLAY is set, even on hybrid X11+Wayland setups (WSLg,
        # and most modern Ubuntu desktops by default use Wayland sessions).
        # This app fundamentally depends on X11 behavior -- global cursor
        # polling (eye-follow, mouse-hunt) and direct window repositioning
        # (drag) are both restricted under Wayland's security model, and
        # even right-click context menus misbehave -- so force xcb unless
        # the user has explicitly set QT_QPA_PLATFORM themselves.
        os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    app = QApplication(sys.argv)
    window = CatWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
