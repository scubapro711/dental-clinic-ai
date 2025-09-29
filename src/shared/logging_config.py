import logging
import sys

def setup_logging(log_level="INFO"):
    """Sets up centralized logging for the application."""
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler("dental_clinic_ai.log")
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    root_logger.setLevel(log_level)

