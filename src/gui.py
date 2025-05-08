
import os
import time
import threading
import PySimpleGUI as sg
from loguru import logger

class QR2KeyApp:
    """
    Main GUI application for QR2Key.
    Provides interface for port selection, connection control, and status display.
    """
    
    def __init__(self, serial_reader, log_path):
        """
        Initialize the GUI application.
        
        Args:
            serial_reader: SerialReader instance
            log_path: Path to log file
        """
        self.serial_reader = serial_reader
        self.log_path = log_path
        self.window = None
        self.is_running = False
        self.update_thread = None
        
        try:
            sg.theme('SystemDefault')
        except AttributeError:
            logger.warning("PySimpleGUI theme function not available in this version")
    
    def create_layout(self):
        """Create the GUI layout"""
        ports = self.serial_reader.get_available_ports()
        port_list = [f"{p['device']} - {p['description']}" for p in ports]
        
        if not port_list:
            port_list = ['No ports available']
        
        layout = [
            [sg.Text('QR2Key - シリアルポート設定', font=('Helvetica', 16))],
            [sg.Text('ポート選択:'), 
             sg.Combo(port_list, default_value=port_list[0] if port_list else '', 
                     size=(40, 1), key='-PORT-', enable_events=True)],
            [sg.Text('ボーレート:'), 
             sg.Input('9600', size=(10, 1), key='-BAUDRATE-')],
            [sg.Button('接続', key='-CONNECT-', size=(10, 1)), 
             sg.Button('切断', key='-DISCONNECT-', size=(10, 1), disabled=True)],
            [sg.Text('状態: 未接続', key='-STATUS-', size=(40, 1))],
            [sg.HorizontalSeparator()],
            [sg.Button('ログを開く', key='-OPEN_LOG-', size=(15, 1)),
             sg.Button('メニューバーに最小化', key='-MINIMIZE-', size=(20, 1)),
             sg.Button('終了', key='-EXIT-', size=(10, 1))],
        ]
        
        return layout
    
    def start(self):
        """Start the GUI application"""
        layout = self.create_layout()
        self.window = sg.Window('QR2Key', layout, finalize=True, icon=None)
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        while True:
            event, values = self.window.read(timeout=100)
            
            if event == sg.WIN_CLOSED or event == '-EXIT-':
                break
            
            elif event == '-CONNECT-':
                port_str = values['-PORT-']
                if port_str and port_str != 'No ports available':
                    port = port_str.split(' - ')[0]
                    
                    try:
                        baudrate = int(values['-BAUDRATE-'])
                        self.serial_reader.config['baudrate'] = baudrate
                    except ValueError:
                        sg.popup_error('ボーレートは数値で入力してください')
                        continue
                    
                    if self.serial_reader.connect(port):
                        self.window['-STATUS-'].update('状態: 接続済み')
                        self.window['-CONNECT-'].update(disabled=True)
                        self.window['-DISCONNECT-'].update(disabled=False)
                    else:
                        sg.popup_error(f'ポート {port} への接続に失敗しました')
            
            elif event == '-DISCONNECT-':
                self.serial_reader.disconnect()
                self.window['-STATUS-'].update('状態: 未接続')
                self.window['-CONNECT-'].update(disabled=False)
                self.window['-DISCONNECT-'].update(disabled=True)
            
            elif event == '-OPEN_LOG-':
                self._open_log_file()
            
            elif event == '-MINIMIZE-':
                self.window.hide()
                import tray
                tray_app = tray.QR2KeyTray(self.serial_reader, self.log_path)
                tray_app.run()
                break
        
        self.is_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        
        if self.serial_reader.is_connected:
            self.serial_reader.disconnect()
        
        if self.window:
            self.window.close()
    
    def _update_loop(self):
        """Update loop for refreshing port list"""
        last_update = 0
        
        while self.is_running and self.window:
            current_time = time.time()
            
            if current_time - last_update > 5:
                if not self.serial_reader.is_connected:
                    ports = self.serial_reader.get_available_ports()
                    port_list = [f"{p['device']} - {p['description']}" for p in ports]
                    
                    if not port_list:
                        port_list = ['No ports available']
                    
                    self.window['-PORT-'].update(values=port_list)
                
                last_update = current_time
            
            time.sleep(0.1)
    
    def _open_log_file(self):
        """Open the log file with the default application"""
        try:
            import subprocess
            subprocess.run(['open', self.log_path], check=True)
            logger.info(f"Opened log file: {self.log_path}")
        except Exception as e:
            logger.error(f"Failed to open log file: {e}")
            sg.popup_error(f'ログファイルを開けませんでした: {e}')
