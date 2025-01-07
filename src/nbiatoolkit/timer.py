import time
from functools import wraps
from nbiatoolkit.logging_config import logger


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(
            f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds"
        )
        return result

    return wrapper
