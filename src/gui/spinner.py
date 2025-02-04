from PyQt6.QtCore import QTimer, QObject, pyqtSignal
import itertools

class Spinner(QObject):
    update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.spinner = itertools.cycle(["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"])
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        self.message = ""

    def _animate(self):
        self.update_signal.emit(f"{next(self.spinner)} {self.message}")

    def start(self, message):
        self.message = message
        self.timer.start(100)

    def stop(self):
        self.timer.stop()
        self.update_signal.emit(f"✓ {self.message}")

