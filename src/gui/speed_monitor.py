import platform
from PyQt6.QtCore import QThread, QObject, pyqtSignal
import psutil
import time

class SpeedMonitorSignals(QObject):
    speed_update = pyqtSignal(float, float)

class SpeedMonitor(QThread):
    def __init__(self, update_interval=None):
        super().__init__()
        self.signals = SpeedMonitorSignals()
        if update_interval is None:
            if platform.system() == 'Windows':
                self.update_interval = 1.0  
            else:
                self.update_interval = 0.2  
        else:
            self.update_interval = update_interval
        self.is_running = True

    def run(self):
        last_total = psutil.net_io_counters()
        last_time = time.time()

        while self.is_running:
            next_time = last_time + self.update_interval
            current_time = time.time()
            sleep_duration = next_time - current_time

            if sleep_duration > 0:
                time.sleep(sleep_duration)

            current_total = psutil.net_io_counters()
            current_time = time.time()

            time_elapsed = current_time - last_time
            if time_elapsed <= 0:
                continue  

            download_speed = (current_total.bytes_recv - last_total.bytes_recv) / time_elapsed
            upload_speed = (current_total.bytes_sent - last_total.bytes_sent) / time_elapsed

            download_mbps = download_speed * 8 / 1_000_000
            upload_mbps = upload_speed * 8 / 1_000_000

            self.signals.speed_update.emit(download_mbps, upload_mbps)

            last_total = current_total
            last_time = current_time

    def stop(self):
        self.is_running = False
        self.wait()  