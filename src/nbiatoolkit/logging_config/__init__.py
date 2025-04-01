from logging import Logger, getLogger
from typing import Any

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

DEFAULT_LOG_LEVEL = "DEBUG"
DEFAULT_LOG_LEVEL = "INFO"


def get_rich_handler(
    console_logging: bool = True,
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
        msg = "This logger only supports console logging for simplicity."
        raise ValueError(msg)

    handler = RichHandler(console=console, show_time=True, show_level=True)
    handler.setFormatter(None)  # Use default Rich formatting
    return handler


def setup_logger(name: str, log_level: str = "INFO") -> Logger:
    """
    Set up a logger with the specified name and log level.

    Args:
        name (str): Name of the logger.
        log_level (str, optional): Log level. Defaults to "INFO".

    Returns
    -------
        logging.Logger: Configured logger instance.
    """
    logger = getLogger(name)
    handler = get_rich_handler(name)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger


class RichProgressBar(Progress):
    """
    A simple subclass of rich.progress.Progress that uses the shared console instance.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa # type: ignore
        super().__init__(
            *args,
            console=console,
            **kwargs,
        )


logger = setup_logger("nbiatoolkit", log_level=DEFAULT_LOG_LEVEL)
# Example usage
if __name__ == "__main__":
    import time

    console.print("Logging Example with Rich")

    # Example Progress Bar Usage
    progress_bar = RichProgressBar()
    with progress_bar as progress:
        task = progress.add_task("Working...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            logger.info("Logging progress...")
            time.sleep(0.1)
