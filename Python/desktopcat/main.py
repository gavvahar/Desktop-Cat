import sys

from PySide6.QtWidgets import QApplication

from desktopcat.window import CatWindow


def main():
    app = QApplication(sys.argv)
    window = CatWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
