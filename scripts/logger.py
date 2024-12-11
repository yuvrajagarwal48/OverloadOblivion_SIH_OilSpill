import logging
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)

# Custom color formatter
class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA
    }

    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        return f"{color}{log_message}{Style.RESET_ALL}"

# Setup logging with colored output
def setup_colored_logging(level=logging.INFO):
    # Create a stream handler
    handler = logging.StreamHandler()
    
    # Create the colored formatter
    formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add the formatter to the handler
    handler.setFormatter(formatter)
    
    # Get the root logger and add the handler
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove any existing handlers to prevent duplicate logging
    logger.handlers.clear()
    logger.addHandler(handler)
    
    return logger
