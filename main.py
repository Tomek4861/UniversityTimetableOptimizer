from ui.config_ui import ConfigApp
import sys
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    window = ConfigApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()




