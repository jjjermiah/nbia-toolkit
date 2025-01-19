import os
from functools import lru_cache, wraps
from inspect import signature
from pathlib import Path
from typing import Callable, Optional, Union


class PathValidator:
    """
    A comprehensive path validator for files and directories.

    Handles validation for existence, readability, writability, executability,
    file extensions, and directory creation. Supports both files and directories
    with explicit restrictions using `file_okay` and `dir_okay`.
    """

    CACHE_SIZE = 128  # Maximum number of unique paths to cache

    def __init__(
        self,
        *arg_names: str,
        exists: bool = False,
        readable: bool = False,
        writable: bool = False,
        executable: bool = False,
        allowed_extensions: Optional[list[str]] = None,
        file_okay: bool = True,
        dir_okay: bool = True,
        mkdirs: bool = False,
    ):
        if not file_okay and not dir_okay:
            raise ValueError("At least one of `file_okay` or `dir_okay` must be True.")

        self.arg_names = arg_names
        self.exists = exists
        self.readable = readable
        self.writable = writable
        self.executable = executable
        self.allowed_extensions = allowed_extensions or []
        self.file_okay = file_okay
        self.dir_okay = dir_okay
        self.mkdirs = mkdirs

    @lru_cache(maxsize=CACHE_SIZE)
    def validate(self, arg_name: str, path: Union[str, Path]):
        """
        Validates a single path argument.

        Parameters:
        - arg_name: The name of the argument being validated.
        - path: The path to validate, as a string or Path object.
        """
        if not isinstance(path, Path):
            path = Path(path)

        if self.exists and not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if path.exists():
            if path.is_dir() and not self.dir_okay:
                raise IsADirectoryError(
                    f"Path '{path}' is a directory, but `dir_okay` is False."
                )
            if path.is_file() and not self.file_okay:
                raise ValueError(f"Path '{path}' is a file, but `file_okay` is False.")

        if self.dir_okay and not path.exists() and self.mkdirs:
            path.mkdir(parents=True, exist_ok=True)

        if self.file_okay and path.is_file() and self.allowed_extensions:
            if path.suffix not in self.allowed_extensions:
                raise ValueError(
                    f"File '{path}' does not have an allowed extension: {self.allowed_extensions}."
                )

        if self.readable and not os.access(path, os.R_OK):
            raise PermissionError(f"Path '{path}' is not readable.")

        if self.writable and not os.access(path, os.W_OK):
            raise PermissionError(f"Path '{path}' is not writable.")

        if self.executable and not os.access(path, os.X_OK):
            raise PermissionError(f"Path '{path}' is not executable.")

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()

            for arg_name in self.arg_names:
                arg_value = bound_args.arguments.get(arg_name)
                if arg_value is None:
                    raise ValueError(
                        f"Argument '{arg_name}' not found in function parameters."
                    )
                self.validate(arg_name, arg_value)

            return func(*args, **kwargs)

        return wrapper
