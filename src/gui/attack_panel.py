from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from .arp_spoofer import ARPSpoofer
import subprocess
import sys
import logging
import re

class AttackPanel(QWidget):
    def __init__(self, device_list):
        super().__init__()
        self.device_list = device_list
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  
        self.setup_ui()
        self.arp_spoofer = ARPSpoofer()
        self.arp_spoofer.status_update.connect(self.update_status)

    def setup_ui(self):
        self.target_label = QLabel("Select a target from the device list")
        self.layout.addWidget(self.target_label)

        self.speed_layout = QHBoxLayout()
        self.speed_label = QLabel("Speed:")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(10)
        self.speed_slider.setValue(5)
        self.speed_layout.addWidget(self.speed_label)
        self.speed_layout.addWidget(self.speed_slider)
        self.layout.addLayout(self.speed_layout)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(80, 30)  
        self.start_button.clicked.connect(self.start_attack)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedSize(80, 30)  
        self.stop_button.clicked.connect(self.stop_attack)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.layout.addLayout(button_layout)

        self.status_label = QLabel("Ready")
        self.layout.addWidget(self.status_label)

    def start_attack(self):
        selected_items = self.device_list.table.selectedItems()
        if selected_items:
            target_ip = selected_items[0].text()
            gateway_ip = self.get_gateway_ip()
            if gateway_ip:
                speed = self.speed_slider.value()
                self.arp_spoofer.start(target_ip, gateway_ip, speed)
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.target_label.setText(f"Attacking: {target_ip}")
            else:
                self.update_status("Failed to detect gateway IP")
        else:
            self.update_status("Please select a target from the device list")

    def stop_attack(self):
        self.arp_spoofer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.target_label.setText("Select a target from the device list")

    def get_gateway_ip(self):
        try:
            if sys.platform.startswith('win'):
                output = subprocess.check_output("ipconfig | findstr /i \"Default Gateway\"", shell=True).decode()
                match = re.search(r"Default Gateway.*: ([\d.]+)", output)
                if match:
                    return match.group(1)
            else:  
                output = subprocess.check_output("ip route | grep default", shell=True).decode()
                match = re.search(r"default via ([\d.]+)", output)
                if match:
                    return match.group(1)
            return None
        except Exception as e:
            logging.error(f"Error detecting gateway IP: {e}")
            self.update_status(f"Error detecting gateway IP: {e}")
            return None

    def update_status(self, message):
        self.status_label.setText(message)
        logging.info(message)

