def get_table_style(is_dark=True):
    return """
    QTableWidget {
        background-color: #1e1e1e;
        color: #ffffff;
        gridline-color: #2a2a2a;
        border: 1px solid #2a2a2a;
    }
    QTableWidget QHeaderView::section {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 5px;
        border: none;
    }
    QTableWidget::item {
        padding: 5px;
        border: none;
    }
    QTableWidget::item:selected {
        background-color: #4a4a4a;
    }
    QHeaderView::section:vertical {
        background-color: #1e1e1e;
        color: #666666;
        padding: 5px;
        border: none;
    }
    QTableCornerButton::section {
        background-color: #1e1e1e;
        border: none;
    }
    """

def get_action_button_style():
    return """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 2px;
        padding: 2px 5px;
        font-weight: bold;
        font-size: 10px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QPushButton:pressed {
        background-color: #3e8e41;
    }
    """

def get_about_dialog_style():
    return """
    QDialog {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    QLabel {
        color: #ffffff;
    }
    QPushButton {
        background-color: #3a3a3a;
        color: #ffffff;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #4a4a4a;
    }
    QPushButton:pressed {
        background-color: #2a2a2a;
    }
    """

dark_style = """
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-size: 12px;
}
QPushButton {
    background-color: #3a3a3a;
    color: #ffffff;
    border: none;
    padding: 5px 10px;
    border-radius: 3px;
}
QPushButton:hover {
    background-color: #4a4a4a;
}
QPushButton:pressed {
    background-color: #2a2a2a;
}
QLabel {
    color: #ffffff;
}
QSlider::groove:horizontal {
    border: 1px solid #3a3a3a;
    height: 4px;
    background: #2a2a2a;
    margin: 0px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #4a4a4a;
    border: 1px solid #5c5c5c;
    width: 10px;
    margin: -3px 0;
    border-radius: 5px;
}
QSlider::handle:horizontal:hover {
    background: #5a5a5a;
}
QTextEdit {
    background-color: #252525;
    color: #ffffff;
    border: 1px solid #2a2a2a;
    border-radius: 3px;
}
QSpinBox {
    background-color: #252525;
    color: #ffffff;
    border: 1px solid #2a2a2a;
    border-radius: 3px;
    padding: 2px;
}
QCheckBox {
    color: #ffffff;
}
QCheckBox::indicator {
    width: 13px;
    height: 13px;
}
QCheckBox::indicator:unchecked {
    background-color: #252525;
    border: 1px solid #3a3a3a;
}
QCheckBox::indicator:checked {
    background-color: #4CAF50;
    border: 1px solid #3a3a3a;
}
"""

def get_scan_button_style(is_scanning):
    if is_scanning:
        return """
        QPushButton {
            background-color: #f44336;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d32f2f;
        }
        QPushButton:pressed {
            background-color: #b71c1c;
        }
        """
    else:
        return """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3e8e41;
        }
        """

