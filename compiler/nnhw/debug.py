import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger('nnhw')

def log(message, level=logging.INFO):
    """Log a message with the specified level."""
    logger.log(level, message)

def debug(message):
    """Log a debug message."""
    log(message, logging.DEBUG)

def info(message):
    """Log an info message."""
    log(message, logging.INFO)

def warning(message):
    """Log a warning message."""
    log(message, logging.WARNING)

def error(message):
    """Log an error message."""
    log(message, logging.ERROR)

def critical(message):
    """Log a critical message."""
    log(message, logging.CRITICAL) 