import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
	BarColumn,
	MofNCompleteColumn,
	Progress,
	TimeElapsedColumn,
	TimeRemainingColumn,
)

# Shared console instance for consistency
console = Console()

DEFAULT_LOG_LEVEL = 'INFO'

logger = setup_logger("nbiatoolkit", log_level=DEFAULT_LOG_LEVEL)


def get_rich_handler(
	name: str,
	log_level: str = 'INFO',
	console_logging: bool = True,
	log_format: str = '%(message)s',
) -> RichHandler:
	"""
	Set up a basic logger using Rich.

	Args:
	        name (str): Name of the logger (not used directly for simplicity).
	        log_level (str, optional): Log level. Defaults to "INFO".
	        console_logging (bool, optional): Enable console logging. Defaults to True.
	        log_format (str, optional): Format of the logs. Defaults to "%(message)s".

	Returns
	-------
	        RichHandler: Configured Rich logger handler.
	"""
	if not console_logging:
		msg = 'This logger only supports console logging for simplicity.'
		raise ValueError(msg)

	level = log_level.upper()
	handler = RichHandler(console=console, level=level, show_time=True, show_level=True)
	handler.setFormatter(None)  # Use default Rich formatting
	return handler


def setup_logger(name: str, log_level: str = 'INFO') -> logging.Logger:
	"""
	Set up a logger with the specified name and log level.

	Args:
	        name (str): Name of the logger.
	        log_level (str, optional): Log level. Defaults to "INFO".

	Returns
	-------
	        logging.Logger: Configured logger instance.
	"""
	logger = logging.getLogger(name)
	handler = get_rich_handler(name, log_level=log_level)
	logger.addHandler(handler)
	logger.setLevel(log_level)
	return logger


class RichProgressBar(Progress):
	"""
	A simple subclass of rich.progress.Progress that uses the shared console instance.
	"""

	def __init__(self, *args, **kwargs) -> None: # noqa
		super().__init__(
			'[progress.description]{task.description}',
			BarColumn(),
			'[progress.percentage]{task.percentage:>3.0f}%',
			MofNCompleteColumn(),
			'Time elapsed:',
			TimeElapsedColumn(),
			'Time remaining:',
			TimeRemainingColumn(compact=True),
			*args,
			console=console,
			**kwargs,
		)


# Example usage
if __name__ == '__main__':
	import time

	# Example Logger Usage
	logger = setup_logger(__name__)

	console.print('Logging Example with Rich')

	# Example Progress Bar Usage
	progress_bar = RichProgressBar()
	with progress_bar as progress:
		task = progress.add_task('Working...', total=100)
		for _ in range(100):
			progress.update(task, advance=1)
			logger.info('Logging progress...')
			time.sleep(0.1)
