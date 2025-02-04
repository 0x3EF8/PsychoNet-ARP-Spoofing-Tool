import sys
import os
import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSystemTrayIcon, QMenu, QApplication, QSplitter
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QThreadPool, QTimer, QSettings
from .network_scanner import NetworkScanner
from .device_list import DeviceList
from .arp_spoofer import ARPSpoofer
from .styles import dark_style, get_scan_button_style
from .spinner import Spinner
from .log_widget import LogWidget
from .settings_dialog import SettingsDialog
from .about_dialog import AboutDialog
from .speed_monitor import SpeedMonitor
import netifaces

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PsychoNet - ARP Spoofing Tool")
        self.setGeometry(100, 100, 800, 400)
        
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.settings = QSettings("0x3EF8", "PsychoNet")
        self.protect_host = self.settings.value("protectHost", False, type=bool)
        self.hide_gateway_and_host = self.settings.value("hideGatewayAndHost", False, type=bool) 
        self.auto_refresh = self.settings.value("autoRefresh", False, type=bool)
        self.auto_refresh_interval = self.settings.value("autoRefreshInterval", 60, type=int)
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self.auto_refresh_scan)
        
        self.setStyleSheet(dark_style)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.setup_ui()
        self.setup_tray_icon()

        self.threadpool = QThreadPool()
        self.arp_spoofers = {}
        self.spinner = Spinner()
        self.spinner.update_signal.connect(self.status_label.setText)

        self.speed_monitor = SpeedMonitor() 
        self.speed_monitor.signals.speed_update.connect(self.update_speed_display)
        self.speed_monitor.start()

        

    def setup_ui(self):
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 0, 10, 0)
        self.scan_button = QPushButton("Scan")
        self.scan_button.setFixedSize(90, 25)
        self.scan_button.clicked.connect(self.scan_network)
        self.scan_button.setStyleSheet(get_scan_button_style(False))
        top_layout.addWidget(self.scan_button)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold;")
        top_layout.addWidget(self.status_label)

        top_layout.addStretch()

        self.log_button = QPushButton("Logs")
        self.log_button.setFlat(True)
        self.log_button.clicked.connect(self.toggle_log)
        top_layout.addWidget(self.log_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.setFlat(True)
        self.settings_button.clicked.connect(self.show_settings)
        top_layout.addWidget(self.settings_button)

        self.about_button = QPushButton("About")
        self.about_button.setFlat(True)
        self.about_button.clicked.connect(self.show_about)
        top_layout.addWidget(self.about_button)
        
        top_layout.addSpacing(5)

        self.layout.addLayout(top_layout)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.device_list = DeviceList(self)
        self.device_list.attack_started.connect(self.start_attack)
        self.device_list.attack_stopped.connect(self.stop_attack)
        left_layout.addWidget(self.device_list)
        self.splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.log_widget = LogWidget()
        right_layout.addWidget(self.log_widget)
        self.splitter.addWidget(right_widget)

        self.splitter.setSizes([700, 300])

    def toggle_log(self):
        if self.log_widget.isVisible():
            self.log_widget.hide()
            self.log_button.setText("Show Log")
        else:
            self.log_widget.show()
            self.log_button.setText("Hide Log")

    def setup_tray_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
            
            show_action = QAction("Show", self)
            quit_action = QAction("Exit", self)
            hide_action = QAction("Hide", self)

            show_action.triggered.connect(self.show)
            hide_action.triggered.connect(self.hide)
            quit_action.triggered.connect(QApplication.instance().quit)

            tray_menu = QMenu()
            tray_menu.addAction(show_action)
            tray_menu.addAction(hide_action)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
        else:
            logging.warning(f"Icon file not found at {icon_path}")
            self.tray_icon = None

    def scan_network(self):
        if self.scan_button.text() == "Scan":
            self.status_label.setText("Scanning network...")
            self.scan_button.setText("Stop")
            self.scan_button.setStyleSheet(get_scan_button_style(True))
            self.spinner.start("Scanning network")
            network_scanner = NetworkScanner()
            network_scanner.signals.result.connect(self.update_device_list)
            network_scanner.signals.finished.connect(self.scan_finished)
            network_scanner.signals.error.connect(self.scan_error)
            network_scanner.signals.progress.connect(self.update_scan_progress)
            network_scanner.signals.log.connect(self.log_widget.append_log)
            self.threadpool.start(network_scanner)
        else:
            self.threadpool.clear()
            self.scan_finished()

    def update_device_list(self, devices):
        self.device_list.update_devices(devices)
        self.log_widget.append_log(f"Scan complete. Found {len(devices)} devices.")

    def scan_finished(self):
        devices_count = self.device_list.table.rowCount()
        self.status_label.setText(f"Scan complete. {devices_count} devices found.")
        self.scan_button.setText("Scan")
        self.scan_button.setStyleSheet(get_scan_button_style(False))
        self.spinner.stop()

    def scan_error(self, error_message):
        self.status_label.setText(f"Scan error: {error_message}")
        self.scan_button.setText("Scan")
        self.scan_button.setStyleSheet(get_scan_button_style(False))
        self.spinner.stop()
        self.log_widget.append_log(f"Scan error: {error_message}")

    def update_scan_progress(self, progress):
        self.status_label.setText(f"Scanning network... {progress}%")

    def start_attack(self, target_ip, speed):
        gateway_ip = self.get_gateway_ip()
        if gateway_ip:
            arp_spoofer = ARPSpoofer()
            arp_spoofer.status_update.connect(self.update_status)
            arp_spoofer.status_update.connect(self.log_widget.append_log)
            arp_spoofer.set_protect_host(self.protect_host)
            arp_spoofer.start(target_ip, gateway_ip, speed)
            self.arp_spoofers[target_ip] = arp_spoofer
            self.log_widget.log_attack_start(target_ip, speed)
        else:
            self.update_status("Failed to detect gateway IP")

    def stop_attack(self, target_ip):
        if target_ip in self.arp_spoofers:
            self.arp_spoofers[target_ip].stop()
            del self.arp_spoofers[target_ip]
            self.log_widget.log_attack_stop(target_ip)

    def get_gateway_ip(self):
        try:
            gateways = netifaces.gateways()
            default_gateway = gateways['default'][netifaces.AF_INET][0]
            return default_gateway
        except Exception as e:
            logging.error(f"Error detecting gateway IP: {e}")
            self.update_status(f"Error detecting gateway IP: {e}")
            return None

    def update_status(self, message):
        self.status_label.setText(message)
        logging.info(message)

    def closeEvent(self, event):
        for spoofer in self.arp_spoofers.values():
            spoofer.stop()
        self.speed_monitor.stop() 
        self.speed_monitor.wait() 
        if self.tray_icon:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "PsychoNet",
                "Application was minimized to tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.accept()

    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec():
            self.apply_settings()

    def apply_settings(self):
        old_hide_gateway_and_host = self.hide_gateway_and_host
        self.protect_host = self.settings.value("protectHost", False, type=bool)
        self.hide_gateway_and_host = self.settings.value("hideGatewayAndHost", True, type=bool)
        self.auto_refresh = self.settings.value("autoRefresh", False, type=bool)
        self.auto_refresh_interval = self.settings.value("autoRefreshInterval", 60, type=int)

        self.update_host_protection(self.protect_host)
        self.log_widget.log_protect_host(self.protect_host)
    
        if old_hide_gateway_and_host != self.hide_gateway_and_host:
            self.log_widget.log_gateway_host_visibility(self.hide_gateway_and_host)
        
        self.device_list.set_hide_gateway_and_host(self.hide_gateway_and_host)
        self.device_list.update_devices(self.device_list.get_devices())
        
        if self.auto_refresh:
            self.auto_refresh_timer.start(self.auto_refresh_interval * 1000)
            self.log_widget.log_auto_refresh_change(True, self.auto_refresh_interval)
        else:
            self.auto_refresh_timer.stop()
            self.log_widget.log_auto_refresh_change(False, 0)

    def update_host_protection(self, protect):
        current_ip = self.get_current_device_ip()
        if current_ip:
            for row in range(self.device_list.table.rowCount()):
                ip_item = self.device_list.table.item(row, 0)
                if ip_item and ip_item.text() == current_ip:
                    action_widget = self.device_list.table.cellWidget(row, 5)
                    if action_widget:
                        action_button = action_widget.findChild(QPushButton)
                        if action_button:
                            action_button.setEnabled(not protect)
                    break
    
        for row in range(self.device_list.table.rowCount()):
            action_widget = self.device_list.table.cellWidget(row, 5)
            if action_widget:
                action_button = action_widget.findChild(QPushButton)
                if action_button:
                    action_button.setEnabled(not protect)

    def get_current_device_ip(self):
        try:
            return netifaces.ifaddresses(netifaces.gateways()['default'][netifaces.AF_INET][1])[netifaces.AF_INET][0]['addr']
        except:
            return None

    def auto_refresh_scan(self):
        if not self.threadpool.activeThreadCount():
            self.log_widget.log_auto_refresh()
            self.scan_network()

    def show_about(self):
        about_dialog = AboutDialog()
        about_dialog.exec()

    def is_protected_host(self, ip):
        return self.protect_host and ip == self.get_current_device_ip()

    def update_speed_display(self, download_speed, upload_speed):
        self.log_widget.update_speed_display(download_speed, upload_speed)

