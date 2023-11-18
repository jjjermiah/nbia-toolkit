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

Configuration
The setup_logger function can be tailored to your needs by adjusting its parameters:
``` python
name: The name of the logger (defaults to root).
log_level: The logging level, e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' (defaults to 'INFO').
log_format: The format of the log messages (defaults to '%(asctime)s | %(name)s | %(levelname)s | %(message)s').
log_file: The name of the log file to which messages will be logged.
log_dir: The directory where the log file will be stored (defaults to the current working directory).
console_logging: Enable logging to the console (defaults to False).

```

Example Usage
Here's an example of how to configure the logger to log DEBUG level messages to both the console and a file, with daily file rotation:

``` python
# Example Logger Setup
logger = setup_logger(
    name=__name__,
    debug=True,
    console_logging=True,
    log_level='DEBUG',
    log_format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    log_file='daily_log.log',
    log_dir='/path/to/log/directory',
)
```

``` python
# Example logging
logger.debug('This is a debug message')
logger.info('Starting the application...')
logger.warning('Warning message')
logger.error('An error has occurred')
logger.critical('Critical issue')
Make sure to replace '/path/to/log/directory' with the actual path where you want your log files to be stored.
```

Error Handling
The setup_logger includes robust error handling to ensure the logging setup process is smooth. The function will raise informative exceptions if issues arise during configuration, such as invalid log level, problems with the log directory (e.g., doesn't exist, permission issues), or issues setting up handlers.

Contributing
If you'd like to contribute to the development of this logger module, please feel free to submit pull requests or open issues with your suggestions and feedback.