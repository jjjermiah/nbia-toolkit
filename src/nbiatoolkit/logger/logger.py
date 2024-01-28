import logging
from logging.handlers import TimedRotatingFileHandler
import os


def setup_logger(
    name: str,
    log_level: str = "INFO",
    console_logging: bool = False,
    log_file: str = None,
    log_dir: str = None,
    log_format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt: str = "%y-%m-%d %H:%M",
) -> logging.Logger:
    """
    Set up a logger object that can be used to log messages to a file and/or console with daily log file rotation.

    Args:
        name (str): The name of the logger.
        log_level (str, optional): The log level. Defaults to 'INFO'.
        console_logging (bool, optional): Whether to log to console. Defaults to False.
        log_file (str, optional): The log file name. Defaults to None.
        log_dir (str, optional): The log directory. Defaults to None.
        log_format (str, optional): The log format. Defaults to '%(asctime)s | %(name)s | %(levelname)s | %(message)s'.
        datefmt (str, optional): The date format. Defaults to '%y-%m-%d %H:%M'.

    Returns:
        logger (logging.Logger): The logger object.
    """
    # Validate log level
    level = getattr(logging, log_level.upper(), None)
    if not isinstance(level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Formatters
    formatter = logging.Formatter(fmt=log_format, datefmt=datefmt)

    # Set up file handler with TimedRotatingFileHandler for daily rotation
    if log_file:
        try:
            # Ensure log directory exists
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, log_file)

            file_handler = TimedRotatingFileHandler(
                log_file, when="midnight", interval=1
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            logger.addHandler(file_handler)
        except Exception as e:
            raise IOError(f"Error setting up file handler for logger: {e}") from e

    # Set up console handler if console_logging is True
    if console_logging:
        try:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(level)
            logger.addHandler(console_handler)
        except Exception as e:
            raise IOError(f"Error setting up console handler for logger: {e}") from e

    return logger


# Example usage
# from nbiatoolkit.utils.logger import setup_logger
# logger = setup_logger(name='my_logger', log_level='DEBUG', console_logging=True, log_file='my_log.log', log_dir='logs')
