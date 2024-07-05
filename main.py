import sys

from PyQt6.QtWidgets import QApplication

from ui.config_ui import ConfigApp


def main():
    app = QApplication(sys.argv + ['-platform', 'windows:darkmode=0'])
    window = ConfigApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
