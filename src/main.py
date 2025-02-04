import sys
import logging
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

VERSION = "0.1.2"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName(f"PsychoNet - ARP Spoofing Tool v{VERSION}")
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)

