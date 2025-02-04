from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QSlider, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from .styles import get_table_style, get_action_button_style

class ReadOnlyTableItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)
        self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)

class DeviceList(QWidget):
    attack_started = pyqtSignal(str, int)
    attack_stopped = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.setup_table()
        self.hide_gateway_and_host = False
        self.devices = []

    def setup_table(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["IP", "MAC", "Name", "Vendor", "Speed", "Action"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 60)
        
        self.table.setStyleSheet(get_table_style())

    def set_hide_gateway_and_host(self, hide):
        self.hide_gateway_and_host = hide

    def update_devices(self, devices):
        self.devices = devices
        attacked_devices = {}
        for row in range(self.table.rowCount()):
            ip = self.table.item(row, 0).text()
            is_attacked = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            if is_attacked:
                attacked_devices[ip] = is_attacked

        gateway_ip = self.main_window.get_gateway_ip()
        current_ip = self.main_window.get_current_device_ip()

        filtered_devices = devices
        if self.hide_gateway_and_host:
            filtered_devices = [d for d in devices if d['ip'] != gateway_ip and d['ip'] != current_ip]
    
        self.table.setRowCount(len(filtered_devices))

        for row, device in enumerate(filtered_devices):
            ip = device['ip']
            keys = ['ip', 'mac', 'name', 'vendor']
            
            for col, key in enumerate(keys):
                item = ReadOnlyTableItem(str(device.get(key, '')))
                self.table.setItem(row, col, item)

            is_gateway_or_host = ip == gateway_ip or ip == current_ip
            is_protected = self.main_window.is_protected_host(ip)

            speed_widget = QWidget()
            speed_layout = QHBoxLayout(speed_widget)
            speed_layout.setContentsMargins(0, 0, 0, 0)
            if not is_gateway_or_host:
                speed_slider = QSlider(Qt.Orientation.Horizontal)
                speed_slider.setMinimum(1)
                speed_slider.setMaximum(10)
                speed_slider.setValue(5)
                speed_slider.setFixedWidth(80)
                speed_label = QLabel("50%")
                speed_slider.valueChanged.connect(lambda value, label=speed_label: label.setText(f"{value*10}%"))
                speed_layout.addWidget(speed_slider)
                speed_layout.addWidget(speed_label)
            self.table.setCellWidget(row, 4, speed_widget)

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            if not is_gateway_or_host and not is_protected:
                action_button = QPushButton("Start" if ip not in attacked_devices else "Stop")
                action_button.setFixedSize(50, 20)
                action_button.setStyleSheet(get_action_button_style())
                action_button.clicked.connect(lambda checked, r=row: self.toggle_attack(r))
                action_layout.addWidget(action_button)
            self.table.setCellWidget(row, 5, action_widget)

            if ip in attacked_devices:
                self.track_attacked_device(ip, True)

    def track_attacked_device(self, ip, is_attacked):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == ip:
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, is_attacked)
                break

    def toggle_attack(self, row):
        ip = self.table.item(row, 0).text()
        action_widget = self.table.cellWidget(row, 5)
        action_button = action_widget.findChild(QPushButton)
        speed_widget = self.table.cellWidget(row, 4)
        speed_slider = speed_widget.findChild(QSlider)

        if action_button.text() == "Start":
            action_button.setText("Stop")
            action_button.setStyleSheet(get_action_button_style().replace(
                "#4CAF50", "#f44336").replace(
                "#45a049", "#d32f2f").replace(
                "#3e8e41", "#b71c1c"))
            self.track_attacked_device(ip, True)
            self.attack_started.emit(ip, speed_slider.value())
        else:
            action_button.setText("Start")
            action_button.setStyleSheet(get_action_button_style())
            self.track_attacked_device(ip, False)
            self.attack_stopped.emit(ip)

    def get_devices(self):
        return self.devices

