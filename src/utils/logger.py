import logging
from logging.handlers import TimedRotatingFileHandler
import os

def setup_logger(
    name: str,
    debug: bool = False,
    console_logging: bool = False,
    log_level: str = 'INFO',
    log_format: str = '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    log_file: str = None,
    log_dir: str = None
) -> logging.Logger:
    """
    Set up a logger object that can be used to log messages to a file and/or console with daily log file rotation.

    Args:
        name (str): The name of the logger. Defaults to 'root'.
        debug (bool): Whether to enable debug logging. Defaults to False.
        console_logging (bool): Whether to enable console logging. Defaults to False.
        log_file (str): The name of the log file if logging to a file. 
        log_level (str): The logging level for the logger. Defaults to 'INFO'.
        log_format (str): The format of the log messages. Defaults to '%(asctime)s | %(name)s | %(levelname)s | %(message)s'.
        log_dir (str): The directory where the log file will be saved.

    Returns:
        logger (logging.Logger): The logger object.
    """
    # Convert log_level string to logging level object
    level = getattr(logging, log_level.upper(), None)
    if not isinstance(level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Formatters
    formatter = logging.Formatter(log_format)

    # Adding file handler with TimedRotatingFileHandler for daily rotation
    if log_file:
        if log_dir:
            # Ensure log directory exists
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                raise IOError(f"Error creating log directory: {log_dir}") from e

            log_file = os.path.join(log_dir, log_file)

        try:
            file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            logger.addHandler(file_handler)
        except Exception as e:
            raise IOError(f"Error setting up file handler for logger: {e}") from e

    if console_logging:
        try:
            # Setup console handler with the same formatter and level
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(level)
            logger.addHandler(console_handler)
        except Exception as e:
            raise IOError(f"Error setting up console handler for logger: {e}") from e

    return logger

# Example Logger Setup

# # Setup your logger
# logger = setup_logger(
#     name=__name__,
#     debug=True,
#     console_logging=True,
#     log_level='DEBUG',
#     log_format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
#     log_file='daily_log.log',
#     log_dir='logs',
# )

# # Example logging
# logger.info('Logger is configured and ready to be used.')