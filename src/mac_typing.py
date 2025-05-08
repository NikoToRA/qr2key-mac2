import time
from pynput.keyboard import Controller, Key
from loguru import logger

class MacTyper:
    """
    Handles keyboard emulation for macOS.
    Types decoded text at the current cursor position.
    """
    
    def __init__(self):
        """Initialize the keyboard controller"""
        self.keyboard = Controller()
        logger.info("MacTyper initialized")
    
    def type_text(self, text):
        """
        Type the given text at the current cursor position.
        Preserves all line breaks and special characters.
        
        Args:
            text: The text to type
        """
        if not text:
            return
        
        try:
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                if line:
                    self.keyboard.type(line)
                    logger.debug(f"Typed line: {line}")
                
                if i < len(lines) - 1:
                    self.keyboard.press(Key.enter)
                    self.keyboard.release(Key.enter)
                    logger.debug("Pressed Enter key")
                
                time.sleep(0.01)
            
            logger.info(f"Successfully typed text ({len(text)} characters)")
        except Exception as e:
            logger.error(f"Error typing text: {e}")
    
    def type_key(self, key):
        """
        Type a specific key.
        
        Args:
            key: The key to type (from pynput.keyboard.Key)
        """
        try:
            self.keyboard.press(key)
            self.keyboard.release(key)
            logger.debug(f"Pressed key: {key}")
        except Exception as e:
            logger.error(f"Error typing key: {e}")
