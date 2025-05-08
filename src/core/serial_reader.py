
import time
import threading
import serial
import serial.tools.list_ports
from loguru import logger

class SerialReader:
    """
    Handles serial port communication for QR code data reading.
    Automatically detects USB-COM ports (CH340/FTDI) and reads Shift-JIS encoded data.
    """
    
    def __init__(self, typer, config):
        """
        Initialize the SerialReader.
        
        Args:
            typer: The keyboard typer instance to send decoded text
            config: Serial configuration dictionary
        """
        self.typer = typer
        self.config = config
        self.serial_port = None
        self.is_connected = False
        self.is_running = False
        self.read_thread = None
        self.buffer = bytearray()
        self.last_read_time = 0
        self.available_ports = []
        
    def get_available_ports(self):
        """
        Get a list of available serial ports, prioritizing CH340 and FTDI devices.
        
        Returns:
            List of port info dictionaries with 'device' and 'description' keys
        """
        try:
            ports = list(serial.tools.list_ports.comports())
            port_list = []
            
            for port in ports:
                if "CH340" in port.description or "FTDI" in port.description:
                    port_list.append({
                        'device': port.device,
                        'description': port.description
                    })
            
            for port in ports:
                if not any(p['device'] == port.device for p in port_list):
                    port_list.append({
                        'device': port.device,
                        'description': port.description
                    })
            
            self.available_ports = port_list
            logger.info(f"Found {len(port_list)} serial ports")
            return port_list
        except Exception as e:
            logger.error(f"Error getting available ports: {e}")
            return []
    
    def connect(self, port=None):
        """
        Connect to a serial port. If port is None, connect to the first available port.
        
        Args:
            port: Optional port device path to connect to
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.is_connected:
            self.disconnect()
        
        try:
            if port is None:
                ports = self.get_available_ports()
                if not ports:
                    logger.error("No serial ports available")
                    return False
                port = ports[0]['device']
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.config.get('baudrate', 9600),
                timeout=self.config.get('timeout', 0.05)
            )
            
            self.is_connected = True
            logger.info(f"Connected to serial port: {port}")
            
            self.start_reading()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to serial port {port}: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the serial port"""
        self.stop_reading()
        
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                logger.info("Disconnected from serial port")
            except Exception as e:
                logger.error(f"Error disconnecting from serial port: {e}")
        
        self.is_connected = False
        self.serial_port = None
    
    def start_reading(self):
        """Start the serial reading thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()
        logger.info("Serial reading thread started")
    
    def stop_reading(self):
        """Stop the serial reading thread"""
        self.is_running = False
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1.0)
        logger.info("Serial reading thread stopped")
    
    def _read_loop(self):
        """Main reading loop that runs in a separate thread"""
        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                data = self.serial_port.read(self.serial_port.in_waiting or 1)
                
                if data:
                    self.buffer.extend(data)
                    self.last_read_time = time.time()
                    
                    if b'\n' in self.buffer:
                        self._process_buffer()
                else:
                    current_time = time.time()
                    if self.buffer and (current_time - self.last_read_time) > self.config.get('timeout', 0.05):
                        self._process_buffer()
                
                time.sleep(0.001)
                
            except Exception as e:
                logger.error(f"Error in serial reading loop: {e}")
                self.is_running = False
                break
    
    def _process_buffer(self):
        """Process the current buffer and send to typer"""
        if not self.buffer:
            return
        
        try:
            encoding = self.config.get('encoding', 'shift_jis')
            error_char = self.config.get('error_char', '�')
            text = self.buffer.decode(encoding, errors='replace')
            
            if '�' in text and error_char != '�':
                text = text.replace('�', error_char)
            
            if text:
                logger.debug(f"Decoded text: {text}")
                self.typer.type_text(text)
        except Exception as e:
            logger.error(f"Error processing buffer: {e}")
        
        self.buffer.clear()
