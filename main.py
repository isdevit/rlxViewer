from concurrent.futures import thread
from PyQt6 import QtCore, QtGui, QtWidgets
import socket
import threading
import server,client
import sys
import trace
import tkinter.messagebox as mess
import tkinter as tk
from tkinter import filedialog
import time
import datetime

# Theme colors
LIGHT_THEME = {
    'bg': '#ffffff',
    'secondary_bg': '#f8fafc',
    'accent': '#2563eb',
    'text': '#0f172a',
    'secondary_text': '#64748b',
    'border': '#e2e8f0',
    'button': '#2563eb',
    'button_hover': '#1d4ed8',
    'button_text': '#ffffff',
    'input_bg': '#ffffff',
    'error': '#ef4444'
}

DARK_THEME = {
    'bg': '#0f172a',
    'secondary_bg': '#1e293b',
    'accent': '#3b82f6',
    'text': '#f8fafc',
    'secondary_text': '#94a3b8',
    'border': '#334155',
    'button': '#3b82f6',
    'button_hover': '#2563eb',
    'button_text': '#ffffff',
    'input_bg': '#1e293b',
    'error': '#ef4444'
}

def get_ip_address():
    """Fetches the WiFi (WLAN) IP instead of Ethernet IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        wlan_ip = s.getsockname()[0]
        s.close()
        return wlan_ip
    except Exception as e:
        return "127.0.0.1"

class ThemeManager:
    def __init__(self):
        self.is_dark_mode = False
        self.current_theme = LIGHT_THEME

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = DARK_THEME if self.is_dark_mode else LIGHT_THEME
        return self.current_theme

class Ui_Setting(object):
    def __init__(self):
        self.setting_window = None
        self.width = 1920
        self.height = 1080
        self.is_record = False
        self.is_auto_blur = False
        self.is_auto_blurwin = False
        self.directory_record_path = ""
        self.app = None
        self.theme_manager = ThemeManager()

    def setupUi(self, Setting):
        Setting.setObjectName("Setting")
        Setting.resize(480, 440)
        
        # Apply theme
        theme = self.theme_manager.current_theme
        Setting.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['bg']};
            }}
            QWidget {{
                font-family: 'Inter', -apple-system, sans-serif;
            }}
        """)
        
        self.centralwidget = QtWidgets.QWidget(parent=Setting)
        self.centralwidget.setObjectName("centralwidget")

        # Title Label
        self.label_title = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_title.setGeometry(QtCore.QRect(30, 20, 420, 40))
        self.label_title.setStyleSheet(f"""
            font: 600 24pt 'Inter';
            color: {theme['text']};
        """)
        self.label_title.setText("Settings")

        # Settings Container
        self.settings_container = QtWidgets.QWidget(parent=self.centralwidget)
        self.settings_container.setGeometry(QtCore.QRect(30, 80, 420, 340))
        self.settings_container.setStyleSheet(f"""
            background-color: {theme['secondary_bg']};
            border-radius: 12px;
            border: 1px solid {theme['border']};
        """)

        # Checkbox Container
        checkbox_container = QtWidgets.QWidget(parent=self.settings_container)
        checkbox_container.setGeometry(QtCore.QRect(20, 20, 380, 160))
        
        checkbox_style = f"""
            QCheckBox {{
                font: 500 13pt 'Inter';
                color: {theme['text']};
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid {theme['border']};
                background: {theme['input_bg']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {theme['accent']};
            }}
            QCheckBox::indicator:checked {{
                background: {theme['accent']};
                border-color: {theme['accent']};
            }}
        """

        # Auto Blur Checkbox
        self.auto_blur = QtWidgets.QCheckBox(parent=checkbox_container)
        self.auto_blur.setGeometry(QtCore.QRect(0, 0, 380, 40))
        self.auto_blur.setStyleSheet(checkbox_style)

        # Auto Blur Window Checkbox
        self.auto_blurwin = QtWidgets.QCheckBox(parent=checkbox_container)
        self.auto_blurwin.setGeometry(QtCore.QRect(0, 50, 380, 40))
        self.auto_blurwin.setStyleSheet(checkbox_style)

        # Record Checkbox
        self.record = QtWidgets.QCheckBox(parent=checkbox_container)
        self.record.setGeometry(QtCore.QRect(0, 100, 380, 40))
        self.record.setStyleSheet(checkbox_style)

        # Resolution Section
        resolution_container = QtWidgets.QWidget(parent=self.settings_container)
        resolution_container.setGeometry(QtCore.QRect(20, 190, 380, 90))

        self.label_display = QtWidgets.QLabel(parent=resolution_container)
        self.label_display.setGeometry(QtCore.QRect(0, 0, 380, 30))
        self.label_display.setStyleSheet(f"""
            font: 500 13pt 'Inter';
            color: {theme['text']};
        """)
        self.label_display.setText("Resolution")

        # Resolution Dropdown
        self.display = QtWidgets.QComboBox(parent=resolution_container)
        self.display.setGeometry(QtCore.QRect(0, 40, 380, 45))
        self.display.setStyleSheet(f"""
            QComboBox {{
                background: {theme['input_bg']};
                color: {theme['text']};
                border: 2px solid {theme['border']};
                border-radius: 8px;
                padding: 0 15px;
                font: 500 13pt 'Inter';
            }}
            QComboBox:hover {{
                border-color: {theme['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox QAbstractItemView {{
                background: {theme['input_bg']};
                color: {theme['text']};
                selection-background-color: {theme['accent']};
                selection-color: white;
                border: 1px solid {theme['border']};
            }}
        """)
        self.display.addItems([
            "1920 x 1080", "1680 x 1050", "1600 x 900", "1440 x 900",
            "1366 x 768", "1280 x 1024", "1280 x 800", "1280 x 720"
        ])

        # Button Container
        button_container = QtWidgets.QWidget(parent=self.settings_container)
        button_container.setGeometry(QtCore.QRect(20, 290, 380, 45))

        # Cancel Button
        self.cancel = QtWidgets.QPushButton(parent=button_container)
        self.cancel.setGeometry(QtCore.QRect(0, 0, 180, 45))
        self.cancel.setStyleSheet(f"""
            QPushButton {{
                background: {theme['secondary_bg']};
                color: {theme['text']};
                border: 2px solid {theme['border']};
                border-radius: 8px;
                font: 600 13pt 'Inter';
            }}
            QPushButton:hover {{
                background: {theme['border']};
            }}
        """)

        # OK Button
        self.ok = QtWidgets.QPushButton(parent=button_container)
        self.ok.setGeometry(QtCore.QRect(200, 0, 180, 45))
        self.ok.setStyleSheet(f"""
            QPushButton {{
                background: {theme['button']};
                color: {theme['button_text']};
                border: none;
                border-radius: 8px;
                font: 600 13pt 'Inter';
            }}
            QPushButton:hover {{
                background: {theme['button_hover']};
            }}
        """)

        Setting.setCentralWidget(self.centralwidget)
        self.ok.clicked.connect(self.quit_OK)
        self.cancel.clicked.connect(self.quit_Cancel)
        self.retranslateUi(Setting)

    def retranslateUi(self, Setting):
        _translate = QtCore.QCoreApplication.translate
        Setting.setWindowTitle(_translate("Setting", "Settings"))
        self.auto_blur.setText(_translate("Setting", "Enable Auto Blur(Slower)"))
        self.auto_blurwin.setText(_translate("Setting","Enable Auto Blur of Window(Faster)"))
        self.record.setText(_translate("Setting", "Record Remote Session"))
        self.ok.setText(_translate("Setting", "OK"))
        self.cancel.setText(_translate("Setting", "Cancel"))
        
    def open_setting_window(self):
        if self.setting_window is None:  
            self.setting_window = QtWidgets.QMainWindow()
            self.setupUi(self.setting_window)
        self.setting_window.show()

    def quit_OK(self):
        if self.setting_window is not None:
            self.get_size_window()
            self.is_record = self.record.isChecked()
            self.is_auto_blur = self.auto_blur.isChecked()
            self.is_auto_blurwin = self.auto_blurwin.isChecked()
            if(self.is_auto_blur==self.is_auto_blurwin):
                self.is_auto_blur=False
            if ( self.is_record):
                file = filedialog.asksaveasfile(defaultextension = '.avi',
                                                filetypes = [
                                                        ("Video file", ".avi"),
                                                        ("Text file", ".txt"),
                                                        ("All files", ".*"),
                                                        ])
                if file is None:
                    return
                self.directory_record_path = file.name
            self.setting_window.close()
        self.setting_window = None  
    def quit_Cancel(self):
        if self.setting_window is not None:  
            self.setting_window.close()
        self.setting_window = None 
    def get_size_window(self):
        list = self.display.currentText().split(" ")
        self.width = (list[0])
        self.height = int(list[2])

class Ui_RemoteDesktop(object):
    def __init__(self):
        self.check_open_connect = False
        self.check_start_remote = False
        self.thread_client = None
        self.thread_server = None
        self.setting_window = Ui_Setting()
        self.theme_manager = ThemeManager()

    def setupUi(self, RemoteDesktop):
        RemoteDesktop.setObjectName("RemoteDesktop")
        RemoteDesktop.resize(1000, 600)
        
        theme = self.theme_manager.current_theme
        RemoteDesktop.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['bg']};
            }}
            QWidget {{
                font-family: 'Inter', -apple-system, sans-serif;
            }}
        """)
        
        self.centralwidget = QtWidgets.QWidget(parent=RemoteDesktop)
        self.centralwidget.setObjectName("centralwidget")

        # Header
        header = QtWidgets.QWidget(parent=self.centralwidget)
        header.setGeometry(QtCore.QRect(0, 0, 1000, 80))
        header.setStyleSheet(f"background: {theme['secondary_bg']};")

        # Title
        self.title_label = QtWidgets.QLabel(parent=header)
        self.title_label.setGeometry(QtCore.QRect(30, 20, 300, 40))
        self.title_label.setStyleSheet(f"""
            font: 600 24pt 'Inter';
            color: {theme['text']};
        """)
        self.title_label.setText("Remote Desktop")

        # Theme Toggle
        self.theme_toggle = QtWidgets.QPushButton(parent=header)
        self.theme_toggle.setGeometry(QtCore.QRect(850, 25, 120, 40))
        self.theme_toggle.setStyleSheet(f"""
            QPushButton {{
                background: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                font: 500 12pt 'Inter';
            }}
            QPushButton:hover {{
                background: {theme['border']};
            }}
        """)
        self.theme_toggle.setText("🌙 Dark" if not self.theme_manager.is_dark_mode else "☀️ Light")
        self.theme_toggle.clicked.connect(self.toggle_theme)

        # Main Content
        content = QtWidgets.QWidget(parent=self.centralwidget)
        content.setGeometry(QtCore.QRect(0, 80, 1000, 520))

        # Host Section (Left)
        host_section = QtWidgets.QWidget(parent=content)
        host_section.setGeometry(QtCore.QRect(30, 20, 460, 480))

        # Host Title
        self.host_title = QtWidgets.QLabel(parent=host_section)
        self.host_title.setGeometry(QtCore.QRect(0, 0, 460, 40))
        self.host_title.setStyleSheet(f"""
            font: 600 18pt 'Inter';
            color: {theme['text']};
        """)
        self.host_title.setText("Allow Remote Control")

        input_style = f"""
            QLineEdit {{
                background: {theme['input_bg']};
                color: {theme['text']};
                border: 2px solid {theme['border']};
                border-radius: 8px;
                padding: 0 15px;
                font: 500 13pt 'Inter';
            }}
            QLineEdit:focus {{
                border-color: {theme['accent']};
            }}
            QLineEdit::placeholder {{
                color: {theme['secondary_text']};
            }}
        """

        label_style = f"""
            font: 500 13pt 'Inter';
            color: {theme['text']};
            margin-top: 10px;
        """

        # IP Section
        self.ip_label = QtWidgets.QLabel(parent=host_section)
        self.ip_label.setGeometry(QtCore.QRect(0, 60, 460, 30))
        self.ip_label.setStyleSheet(label_style)
        self.ip_label.setText("Your IP Address")

        self.your_ip = QtWidgets.QLabel(parent=host_section)
        self.your_ip.setGeometry(QtCore.QRect(0, 95, 460, 45))
        self.your_ip.setStyleSheet(input_style.replace("QLineEdit", "QLabel") + "qproperty-alignment: AlignVCenter;")

        # Port Section
        self.port_label = QtWidgets.QLabel(parent=host_section)
        self.port_label.setGeometry(QtCore.QRect(0, 160, 460, 30))
        self.port_label.setStyleSheet(label_style)
        self.port_label.setText("Port")

        self.my_port = QtWidgets.QLineEdit(parent=host_section)
        self.my_port.setGeometry(QtCore.QRect(0, 195, 460, 45))
        self.my_port.setStyleSheet(input_style)
        self.my_port.setPlaceholderText("Enter Port")

        # Open Connect Button
        self.open_connect = QtWidgets.QPushButton(parent=host_section)
        self.open_connect.setGeometry(QtCore.QRect(0, 260, 460, 45))
        self.open_connect.setStyleSheet(f"""
            QPushButton {{
                background: {theme['button']};
                color: {theme['button_text']};
                border: none;
                border-radius: 8px;
                font: 600 13pt 'Inter';
            }}
            QPushButton:hover {{
                background: {theme['button_hover']};
            }}
        """)

        # Client Section (Right)
        client_section = QtWidgets.QWidget(parent=content)
        client_section.setGeometry(QtCore.QRect(510, 20, 460, 480))

        # Client Title
        self.client_title = QtWidgets.QLabel(parent=client_section)
        self.client_title.setGeometry(QtCore.QRect(0, 0, 460, 40))
        self.client_title.setStyleSheet(f"""
            font: 600 18pt 'Inter';
            color: {theme['text']};
        """)
        self.client_title.setText("Control Remote Desktop")

        # Server IP
        self.server_ip_label = QtWidgets.QLabel(parent=client_section)
        self.server_ip_label.setGeometry(QtCore.QRect(0, 60, 460, 30))
        self.server_ip_label.setStyleSheet(label_style)
        self.server_ip_label.setText("Server IP")

        self.server_ip = QtWidgets.QLineEdit(parent=client_section)
        self.server_ip.setGeometry(QtCore.QRect(0, 95, 460, 45))
        self.server_ip.setStyleSheet(input_style)
        self.server_ip.setPlaceholderText("Enter Server IP")

        # Server Port
        self.server_port_label = QtWidgets.QLabel(parent=client_section)
        self.server_port_label.setGeometry(QtCore.QRect(0, 160, 460, 30))
        self.server_port_label.setStyleSheet(label_style)
        self.server_port_label.setText("Port")

        self.port_server = QtWidgets.QLineEdit(parent=client_section)
        self.port_server.setGeometry(QtCore.QRect(0, 195, 460, 45))
        self.port_server.setStyleSheet(input_style)
        self.port_server.setPlaceholderText("Enter Port")

        # Action Buttons
        button_style = f"""
            QPushButton {{
                background: {theme['secondary_bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                font: 500 13pt 'Inter';
            }}
            QPushButton:hover {{
                background: {theme['border']};
            }}
        """

        self.Setting = QtWidgets.QPushButton(parent=client_section)
        self.Setting.setGeometry(QtCore.QRect(0, 260, 225, 45))
        self.Setting.setStyleSheet(button_style)

        self.Send_file = QtWidgets.QPushButton(parent=client_section)
        self.Send_file.setGeometry(QtCore.QRect(235, 260, 225, 45))
        self.Send_file.setStyleSheet(button_style)

        # Connect Button
        self.connect = QtWidgets.QPushButton(parent=client_section)
        self.connect.setGeometry(QtCore.QRect(0, 315, 460, 45))
        self.connect.setStyleSheet(f"""
            QPushButton {{
                background: {theme['button']};
                color: {theme['button_text']};
                border: none;
                border-radius: 8px;
                font: 600 13pt 'Inter';
            }}
            QPushButton:hover {{
                background: {theme['button_hover']};
            }}
        """)

        RemoteDesktop.setCentralWidget(self.centralwidget)

        # Connect buttons
        self.open_connect.clicked.connect(self.open_click)
        self.connect.clicked.connect(self.connect_click)
        self.Send_file.clicked.connect(self.sendfile_click)
        self.Setting.clicked.connect(self.setting_window.open_setting_window)

        self.retranslateUi(RemoteDesktop)

    def toggle_theme(self):
        theme = self.theme_manager.toggle_theme()
        self.theme_toggle.setText("🌙 Dark" if not self.theme_manager.is_dark_mode else "☀️ Light")
        # Update all widget styles with new theme
        self.setupUi(self.centralwidget.parent())

    def sendfile_click(self):
        if self.check_start_remote:
            self.app.start_sendfile()
        else: pass

    def open_click(self):
        if not self.check_open_connect:
            self.start_connect()
        else:
            self.close_connect()
            self.open_connect.setText("Open Connect")

    def connect_click(self):
        if not self.check_start_remote:
            self.start_remote()
        else:
            self.close_remote()
            self.connect.setText("Connect")

    def retranslateUi(self, RemoteDesktop):
        _translate = QtCore.QCoreApplication.translate
        RemoteDesktop.setWindowTitle(_translate("RemoteDesktop", "Remote Desktop"))
        self.title_label.setText(_translate("RemoteDesktop", "Remote Desktop"))
        self.ip_label.setText(_translate("RemoteDesktop", "Your IP Address"))
        self.port_label.setText(_translate("RemoteDesktop", "Port"))
        self.my_port.setPlaceholderText(_translate("RemoteDesktop", "Enter Port"))
        self.your_ip.setText(_translate("RemoteDesktop", get_ip_address()))
        self.open_connect.setText(_translate("RemoteDesktop", "Open Connect"))
        self.client_title.setText(_translate("RemoteDesktop", "Control Remote Desktop"))
        self.server_ip_label.setText(_translate("RemoteDesktop", "Server IP"))
        self.server_port_label.setText(_translate("RemoteDesktop", "Port"))
        self.Send_file.setText(_translate("RemoteDesktop", "Send File"))
        self.Setting.setText(_translate("RemoteDesktop", "Setting"))
        self.connect.setText(_translate("RemoteDesktop", "Connect"))
        self.server_ip.setPlaceholderText(_translate("RemoteDesktop", "Enter IP"))
        self.port_server.setPlaceholderText(_translate("RemoteDesktop", "Enter Port"))

    def start_connect(self):
        if not self.check_start_remote and not self.check_open_connect:
            self.check_open_connect = True
            self.run_server()
            self.open_connect.setText("Close Connect")
        else:
            mess.showerror(title = "Error",
                    message = "You can't open the connect because you're remote.")
            
    def start_remote(self): 
        if not self.check_start_remote and not self.check_open_connect:
            self.check_start_remote = True
            self.run_client()
            self.connect.setText("Close Connect")
        else:
            mess.showerror(title = "Error",
                    message = "You can't  become remote because you're open to connect.")

    def kill_thread(self, app):
        self.app.running = False

    def close_connect(self):
        self.check_open_connect = False
        self.kill_thread(self.app)

    def close_remote(self):
        self.check_start_remote = False
        self.kill_thread(self.app)

    def thread_run_server(self):
        self.app = server.Server()
        self.app.port = int(self.my_port.text())
        self.app.is_auto_blur = self.setting_window.is_auto_blur
        self.app.is_auto_blurwin = self.setting_window.is_auto_blurwin
        self.app.start_server()

    def run_server(self):
        self.thread_server = threading.Thread(target=self.thread_run_server)
        self.thread_server.daemon = True
        self.thread_server.start()

    def thread_run_client(self):
        self.app = client.Client()
        self.app.host = self.server_ip.text()
        self.app.port = int(self.port_server.text())
        self.app.record = self.setting_window.is_record
        self.app.width_window = self.setting_window.width
        self.app.height_window = self.setting_window.height
        if ( self.app.record):
            self.app.filename_record = self.setting_window.directory_record_path
        print( self.app.host,  self.app.port,  self.app.width_window,  self.app.height_window, self.app.record)
        print( self.app.filename_record)
        self.app.start_client()

    def run_client(self):
        self.thread_client =  threading.Thread(target=self.thread_run_client)
        self.thread_client.daemon = True
        self.thread_client.start()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    RemoteDesktop = QtWidgets.QMainWindow()
    ui = Ui_RemoteDesktop()
    ui.setupUi(RemoteDesktop)
    RemoteDesktop.show()
    sys.exit(app.exec())  
