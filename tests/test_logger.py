import logging
import os
from logging.handlers import TimedRotatingFileHandler

import pytest
from nbiatoolkit.logger.logger import setup_logger


def test_setup_logger_name():
    # Test case 1: Verify that the logger is created with the correct name
    logger = setup_logger("test_logger1")
    assert logger.name == "test_logger1"


def test_setup_logger_level():
    # Test case 2: Verify that the logger level is set correctly
    logger = setup_logger("test_logger2", log_level="DEBUG")
    assert logger.level == logging.DEBUG


def test_setup_logger_console_logging():
    # Test case 3: Verify that the logger logs to console when console_logging is True
    logger = setup_logger("test_logger3", console_logging=True)
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    # close the file handler
    logger.handlers[0].close()


def test_setup_logger_log_file():
    # Test case 4: Verify that the logger logs to file when log_file is provided
    log_file = "test.log"
    logger = setup_logger("test_logger4", log_file=log_file)
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], TimedRotatingFileHandler)
    assert logger.handlers[0].baseFilename == os.path.abspath(log_file)

    # close the file handler
    logger.handlers[0].close()


def test_setup_logger_log_dir():
    # Test case 5: Verify that the logger logs to file in the specified log_dir
    log_file = "test.log"
    log_dir = "logdir"
    logger = setup_logger("test_logger5", log_file=log_file, log_dir=log_dir)
    assert isinstance(logger.handlers[0], TimedRotatingFileHandler)
    assert logger.handlers[0].baseFilename == os.path.abspath(
        os.path.join(log_dir, log_file)
    )

    # close the file handler
    logger.handlers[0].close()


def test_invalid_log_level():
    # Test case 6: Verify that an error is raised for an invalid log level
    try:
        setup_logger("test_logger6", log_level="INVALID")
    except ValueError as e:
        assert str(e) == "Invalid log level: INVALID"


def test_invalid_log_file():
    # Test case 7: Verify that an error is raised for an invalid log file
    with pytest.raises(IOError):
        setup_logger("test_logger7", log_file="/invalid/log/file.log")
