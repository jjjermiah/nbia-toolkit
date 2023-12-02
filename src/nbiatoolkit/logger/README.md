# Logger Module

## Overview

The `logger` module provides a flexible and easy-to-use logging setup for Python applications. It allows logging messages to both the console and a rotating log file that changes daily. With minimal configuration required, the module can be readily incorporated into any project to enhance its logging capabilities.

## Features

- Console and file logging with independently set log levels
- Daily rotation of log files to prevent unrestricted growth
- Customizable log format and log level
- Simple to set up and use

## Installation

To use this logger module, copy the `logger.py` file to your project directory.

## Setup

Import the `setup_logger` function from the `logger` module in your Python script:

``` python
from logger import setup_logger
```

# Configuration
The setup_logger function can be tailored to your needs by adjusting its parameters:
``` python
name (str): The name of the logger.
log_level (str, optional): The log level. Defaults to 'INFO'.
console_logging (bool, optional): Whether to log to console. Defaults to False.
log_file (str, optional): The log file name. Defaults to None.
log_dir (str, optional): The log directory. Defaults to None.
log_format (str, optional): The log format. Defaults to '%(asctime)s | %(name)s | %(levelname)s | %(message)s'.
datefmt (str, optional): The date format. Defaults to '%y-%m-%d %H:%M'.

```

# Example Usage
Here's an example of how to configure the logger to log DEBUG level messages to both the console and a file, with daily file rotation:

``` python
logger = setup_logger(
    name='my_logger',
    log_level='DEBUG',
    console_logging=True,
    log_file='my_log.log',
    log_dir='logs')
# log_file can include directories, but must be a relative path
# log dir does not need to exist, it will be created if it doesn't exist
```

``` python
# Example logging
logger.debug('This is a debug message')
logger.info('Starting the application...')
logger.warning('Warning message')
logger.error('An error has occurred')
logger.critical('Critical issue')
```

# Error Handling
The setup_logger includes robust error handling to ensure the logging setup process is smooth. The function will raise informative exceptions if issues arise during configuration, such as invalid log level, problems with the log directory (e.g., doesn't exist, permission issues), or issues setting up handlers.

# Contributing
If you'd like to contribute to the development of this logger module, please feel free to submit pull requests or open issues with your suggestions and feedback.