from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIntValidator

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PsychoNet Settings")
        self.setModal(True)
        
        self.settings = QSettings("0x3EF8", "PsychoNet")
        
        layout = QVBoxLayout(self)
        
        protect_host_layout = QHBoxLayout()
        protect_host_label = QLabel("Enable ARP Spoofing Protection:")
        self.protect_host_checkbox = QCheckBox()
        self.protect_host_checkbox.setChecked(self.settings.value("protectHost", False, type=bool))
        protect_host_layout.addWidget(protect_host_label)
        protect_host_layout.addWidget(self.protect_host_checkbox)
        layout.addLayout(protect_host_layout)
        
        hide_gh_layout = QHBoxLayout()
        hide_gh_label = QLabel("Hide Gateway and Host:")
        self.hide_gh_checkbox = QCheckBox()
        self.hide_gh_checkbox.setChecked(self.settings.value("hideGatewayAndHost", False, type=bool)) 
        hide_gh_layout.addWidget(hide_gh_label)
        hide_gh_layout.addWidget(self.hide_gh_checkbox)
        layout.addLayout(hide_gh_layout)
        
        auto_refresh_layout = QHBoxLayout()
        auto_refresh_label = QLabel("Auto Refresh:")
        self.auto_refresh_checkbox = QCheckBox()
        self.auto_refresh_checkbox.setChecked(self.settings.value("autoRefresh", False, type=bool))
        auto_refresh_layout.addWidget(auto_refresh_label)
        auto_refresh_layout.addWidget(self.auto_refresh_checkbox)
        layout.addLayout(auto_refresh_layout)
        
        auto_refresh_interval_layout = QHBoxLayout()
        auto_refresh_interval_label = QLabel("Auto Refresh Interval (seconds):")
        self.auto_refresh_interval_input = QLineEdit()
        self.auto_refresh_interval_input.setValidator(QIntValidator(10, 3600))
        self.auto_refresh_interval_input.setText(str(self.settings.value("autoRefreshInterval", 60, type=int)))
        auto_refresh_interval_layout.addWidget(auto_refresh_interval_label)
        auto_refresh_interval_layout.addWidget(self.auto_refresh_interval_input)
        layout.addLayout(auto_refresh_interval_layout)
        
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def accept(self):
        self.settings.setValue("protectHost", self.protect_host_checkbox.isChecked())
        self.settings.setValue("hideGatewayAndHost", self.hide_gh_checkbox.isChecked())
        self.settings.setValue("autoRefresh", self.auto_refresh_checkbox.isChecked())
        self.settings.setValue("autoRefreshInterval", int(self.auto_refresh_interval_input.text()))
        self.settings.sync()
        super().accept()

