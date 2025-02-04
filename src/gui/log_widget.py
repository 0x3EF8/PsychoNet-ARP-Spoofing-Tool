from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, QObject
from datetime import datetime

class LogSignals(QObject):
    update = pyqtSignal(str)

class LogWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        header_layout = QHBoxLayout()
        
        attack_log_label = QLabel("Logs")
        header_layout.addWidget(attack_log_label)
        
        header_layout.addStretch()
        
        self.speed_label = QLabel("S ↓0.00 ↑0.00") # Update 1
        header_layout.addWidget(self.speed_label)
        
        self.layout.addLayout(header_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

        self.signals = LogSignals()
        self.signals.update.connect(self.append_log)

    def append_log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def clear_log(self):
        self.log_text.clear()

    def log_network_scan(self, devices):
        self.append_log(f"Network scan completed. Found {len(devices)} devices.")
        for device in devices:
            self.append_log(f"  - IP: {device['ip']}, MAC: {device['mac']}, Name: {device['name']}, Vendor: {device['vendor']}")

    def log_auto_refresh(self):
        self.append_log("Auto-refresh scan initiated.")

    def log_attack_start(self, target_ip, speed):
        self.append_log(f"Started ARP spoofing attack on {target_ip} with speed {speed}")

    def log_attack_stop(self, target_ip):
        self.append_log(f"Stopped ARP spoofing attack on {target_ip}")

    def log_protect_host(self, status):
        self.append_log(f"Protect Host: {'Enabled' if status else 'Disabled'}")

    def log_auto_refresh_change(self, status, interval):
        if status:
            self.append_log(f"Auto-refresh enabled with interval: {interval} seconds")
        else:
            self.append_log("Auto-refresh disabled")

    def log_gateway_host_visibility(self, hidden):
        self.append_log(f"Gateway and Host visibility: {'Hidden' if hidden else 'Visible'}")

    def update_speed_display(self, download_speed, upload_speed):
        self.speed_label.setText(f"S ↓{download_speed:.2f} ↑{upload_speed:.2f}") # Update 2

    def log_speed_test_result(self, download_speed, upload_speed):
        self.append_log(f"Speed Test Result: Download: {download_speed:.2f} Mbps, Upload: {upload_speed:.2f} Mbps")

