from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QIcon
from .styles import get_about_dialog_style
import os

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About PsychoNet")
        self.setFixedSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(get_about_dialog_style())
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')
        if os.path.exists(icon_path):
            logo = QPixmap(icon_path)
            logo_label = QLabel()
            logo_label.setPixmap(logo.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)

            self.setWindowIcon(QIcon(icon_path))

        title_label = QLabel("PsychoNet - ARP Spoofing Tool")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        version_label = QLabel("Version 0.1.2")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        description = """
        <p style='text-align: center;'>
        PsychoNet is a simple ARP spoofing tool for educational purposes.
        Use responsibly and only on networks you own or have permission to test.
        </p>
        """
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        dev_label = QLabel("Developer: 0x3EF8")
        dev_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(dev_label)

        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(button_layout)

