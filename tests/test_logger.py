import logging
import os
from logging.handlers import TimedRotatingFileHandler
from nbiatoolkit.logger.logger import setup_logger

def test_setup_logger_name():
    # Test case 1: Verify that the logger is created with the correct name
    logger = setup_logger("test_logger")
    assert logger.name == "test_logger"

def test_setup_logger_level():
    # Test case 2: Verify that the logger level is set correctly
    logger = setup_logger("test_logger", log_level="DEBUG")
    assert logger.level == logging.DEBUG

def test_setup_logger_console_logging():
    # Test case 3: Verify that the logger logs to console when console_logging is True
    logger = setup_logger("test_logger", console_logging=True)
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)

def test_setup_logger_log_file():
    # Test case 4: Verify that the logger logs to file when log_file is provided
    log_file = "test.log"
    logger = setup_logger("test_logger", log_file=log_file)
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], TimedRotatingFileHandler)
    assert logger.handlers[0].baseFilename == os.path.abspath(log_file)

def test_setup_logger_log_dir():
    # Test case 5: Verify that the logger logs to file in the specified log_dir
    log_file = "test.log"
    log_dir = "logs"
    logger = setup_logger("test_logger", log_file=log_file, log_dir=log_dir)
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], TimedRotatingFileHandler)
    assert logger.handlers[0].baseFilename == os.path.abspath(os.path.join(log_dir, log_file))
