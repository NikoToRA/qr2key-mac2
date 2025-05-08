
import os
import sys
import subprocess
import rumps
from loguru import logger

class QR2KeyTray(rumps.App):
    """
    macOS menu bar application for QR2Key.
    Provides menu options for connection control and application management.
    """
    
    def __init__(self, serial_reader, log_path):
        """
        Initialize the tray application.
        
        Args:
            serial_reader: SerialReader instance
            log_path: Path to log file
        """
        super(QR2KeyTray, self).__init__("QR2Key", icon=None)
        
        self.serial_reader = serial_reader
        self.log_path = log_path
        
        self.menu = [
            rumps.MenuItem("接続状態: 未接続", callback=None),
            None,  # Separator
            rumps.MenuItem("接続開始", callback=self.toggle_connection),
            rumps.MenuItem("ログを開く", callback=self.open_log),
            rumps.MenuItem("設定を開く", callback=self.open_settings),
            None,  # Separator
            rumps.MenuItem("自動起動を設定", callback=self.toggle_autostart),
            None,  # Separator
            rumps.MenuItem("終了", callback=self.quit_app)
        ]
        
        self._update_connection_status()
    
    def _update_connection_status(self):
        """Update the connection status in the menu"""
        if self.serial_reader.is_connected:
            self.menu["接続状態: 未接続"].title = "接続状態: 接続済み"
            self.menu["接続開始"].title = "接続停止"
        else:
            self.menu["接続状態: 接続済み"].title = "接続状態: 未接続"
            self.menu["接続開始"].title = "接続開始"
    
    @rumps.clicked("接続開始")
    def toggle_connection(self, sender):
        """Toggle serial connection"""
        if self.serial_reader.is_connected:
            self.serial_reader.disconnect()
            logger.info("Disconnected from serial port via menu bar")
        else:
            if self.serial_reader.connect():
                logger.info("Connected to serial port via menu bar")
            else:
                rumps.notification(
                    title="QR2Key",
                    subtitle="接続エラー",
                    message="シリアルポートに接続できませんでした。設定を確認してください。"
                )
        
        self._update_connection_status()
    
    @rumps.clicked("ログを開く")
    def open_log(self, _):
        """Open the log file"""
        try:
            subprocess.run(['open', self.log_path], check=True)
            logger.info(f"Opened log file: {self.log_path}")
        except Exception as e:
            logger.error(f"Failed to open log file: {e}")
            rumps.notification(
                title="QR2Key",
                subtitle="エラー",
                message=f"ログファイルを開けませんでした: {e}"
            )
    
    @rumps.clicked("設定を開く")
    def open_settings(self, _):
        """Open the settings GUI"""
        try:
            app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
            subprocess.Popen([sys.executable, app_path])
            logger.info("Opened settings GUI")
        except Exception as e:
            logger.error(f"Failed to open settings: {e}")
            rumps.notification(
                title="QR2Key",
                subtitle="エラー",
                message=f"設定画面を開けませんでした: {e}"
            )
    
    @rumps.clicked("自動起動を設定")
    def toggle_autostart(self, sender):
        """Toggle automatic startup setting"""
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        plist_path = os.path.join(launch_agents_dir, "com.qr2key.app.plist")
        
        if os.path.exists(plist_path):
            try:
                os.remove(plist_path)
                sender.title = "自動起動を有効化"
                logger.info("Disabled autostart")
                rumps.notification(
                    title="QR2Key",
                    subtitle="自動起動設定",
                    message="自動起動を無効化しました"
                )
            except Exception as e:
                logger.error(f"Failed to disable autostart: {e}")
                rumps.notification(
                    title="QR2Key",
                    subtitle="エラー",
                    message=f"自動起動の無効化に失敗しました: {e}"
                )
        else:
            try:
                os.makedirs(launch_agents_dir, exist_ok=True)
                
                if getattr(sys, 'frozen', False):
                    app_path = os.path.abspath(sys.executable)
                else:
                    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
                
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.qr2key.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{app_path}</string>
        <string>--tray</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
"""
                
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
                
                sender.title = "自動起動を無効化"
                logger.info("Enabled autostart")
                rumps.notification(
                    title="QR2Key",
                    subtitle="自動起動設定",
                    message="自動起動を有効化しました"
                )
            except Exception as e:
                logger.error(f"Failed to enable autostart: {e}")
                rumps.notification(
                    title="QR2Key",
                    subtitle="エラー",
                    message=f"自動起動の有効化に失敗しました: {e}"
                )
    
    @rumps.clicked("終了")
    def quit_app(self, _):
        """Quit the application"""
        if self.serial_reader.is_connected:
            self.serial_reader.disconnect()
        
        logger.info("Application exiting via menu bar")
        rumps.quit_application()
