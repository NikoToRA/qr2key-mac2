
import os
import json
import sys
from pathlib import Path
from loguru import logger

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.serial_reader import SerialReader
from mac_typing import MacTyper
import gui
import tray

def setup_logging():
    """Configure logging with loguru"""
    log_dir = os.path.expanduser("~/Library/Logs/QR2Key")
    os.makedirs(log_dir, exist_ok=True)
    
    log_path = os.path.join(log_dir, "app.log")
    
    logger.remove()  # Remove default handler
    logger.add(log_path, rotation="10 MB", level="INFO", 
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
    
    logger.info("QR2Key application started")
    return log_path

def load_config():
    """Load configuration from config.json"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {
            "serial": {
                "baudrate": 9600,
                "timeout": 0.05,
                "encoding": "shift_jis",
                "error_char": "�"
            },
            "app": {
                "log_path": "~/Library/Logs/QR2Key/app.log",
                "log_level": "INFO"
            }
        }

def main():
    """Main application entry point"""
    log_path = setup_logging()
    
    config = load_config()
    
    typer = MacTyper()
    serial_reader = SerialReader(typer, config["serial"])
    
    if len(sys.argv) > 1 and sys.argv[1] == "--tray":
        app = tray.QR2KeyTray(serial_reader, log_path)
        app.run()
    else:
        app = gui.QR2KeyApp(serial_reader, log_path)
        app.start()

if __name__ == "__main__":
    main()
