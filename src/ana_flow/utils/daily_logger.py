import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import sys

class DailyLogger:
    """
    A logging utility class that creates new log files each day.
    Automatically rotates log files based on date and maintains log formatting.
    """
    
    def __init__(self, name='default', log_dir='logs', save_name='run', level=logging.INFO, 
                 format_string=None, max_days=30):
        """
        Initialize the daily logger.
        
        Args:
            name (str): Logger name
            log_dir (str): Directory to store log files
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format_string (str): Custom log format string
            max_days (int): Maximum number of days to keep log files
        """
        self.name = name
        self.log_dir = log_dir
        self.save_name = save_name
        self.level = level
        self.max_days = max_days
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Default log format
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Clear any existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(format_string)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Create daily rotating file handler
        log_file_path = os.path.join(log_dir, f'{save_name}.log')
        file_handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when='midnight',
            interval=1,
            backupCount=max_days,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # Set custom suffix for rotated files
        file_handler.suffix = "%Y-%m-%d.log"
        file_handler.namer = self._namer
        
        self.logger.addHandler(file_handler)
    
    def _namer(self, default_name):
        """
        Custom naming function for rotated log files.
        Creates files with format: name.YYYY-MM-DD.log
        """
        base_name = os.path.basename(default_name)
        name_parts = base_name.split('.')
        if len(name_parts) >= 2:
            # Extract date from the default name and create custom format
            date_part = name_parts[-2]  # Get the date part
            return os.path.join(self.log_dir, f"{self.name}.{date_part}.log")
        return default_name
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)
    
    def exception(self, message):
        """Log exception with traceback"""
        self.logger.exception(message)
    
    def get_logger(self):
        """Get the underlying logger object for advanced usage"""
        return self.logger


# Example usage and demonstration
if __name__ == "__main__":
    # Create a daily logger
    logger = DailyLogger(
        name='example_app',
        log_dir='logs',
        level=logging.DEBUG,
        max_days=7
    )
    
    # Log some messages
    logger.info("Daily logger initialized successfully!")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Log with custom format
    custom_logger = DailyLogger(
        name='custom_format',
        format_string='%(asctime)s | %(levelname)-8s | %(message)s',
        max_days=14
    )
    
    custom_logger.info("Custom format logger created!")
    custom_logger.info("This message uses custom formatting") 