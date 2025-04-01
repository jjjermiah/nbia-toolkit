import os
from functools import lru_cache, wraps
from inspect import signature
from pathlib import Path
from typing import Callable, Optional, Union
from dataclasses import dataclass

@dataclass
class PathValidator:
    """A comprehensive path validator for files and directories.
    
    This decorator validates file and directory paths in function arguments,
    ensuring they meet specified requirements like existence, permissions,
    file types, etc. It can be applied to any function that accepts paths.
    
    Parameters
    ----------
    arg_names : tuple[str, ...]
        Names of the function arguments that should be validated as paths.
    exists : bool, default False
        If True, paths must exist. If False, non-existent paths are allowed.
    readable : bool, default False
        If True, paths must be readable.
    writable : bool, default False
        If True, paths must be writable.
    executable : bool, default False
        If True, paths must be executable.
    allowed_extensions : list[str], optional
        List of allowed file extensions (e.g., ['.txt', '.csv']). If provided,
        file paths must have one of these extensions.
    file_okay : bool, default True
        If True, file paths are allowed. If False, file paths will raise an error.
    dir_okay : bool, default True
        If True, directory paths are allowed. If False, directory paths will 
        raise an error.
    mkdirs : bool, default False
        If True, non-existent directories will be created automatically.
    CACHE_SIZE : int, default 128
        Maximum number of validated paths to cache to avoid repetitive validation.
    
    Examples
    --------
    Basic usage with a single path argument:
    
    >>> @PathValidator(arg_names=('config_path',), exists=True)
    ... def load_config(config_path):
    ...     with open(config_path) as f:
    ...         return f.read()
    
    Validating multiple paths with different requirements:
    
    >>> @PathValidator(
    ...     arg_names=('input_file', 'output_dir'),
    ...     exists=True,
    ...     file_okay=True,
    ...     dir_okay=True
    ... )
    ... def process_file(input_file, output_dir):
    ...     # Process the input file and save results to output_dir
    ...     pass
    
    Restricting to specific file extensions:
    
    >>> @PathValidator(
    ...     arg_names=('image_path',),
    ...     exists=True,
    ...     allowed_extensions=['.png', '.jpg', '.jpeg']
    ... )
    ... def process_image(image_path):
    ...     # Process only PNG or JPEG images
    ...     pass
    
    Auto-creating directories:
    
    >>> @PathValidator(
    ...     arg_names=('output_dir',),
    ...     dir_okay=True,
    ...     file_okay=False,
    ...     mkdirs=True
    ... )
    ... def save_results(output_dir, data):
    ...     # output_dir will be created if it doesn't exist
    ...     with open(f"{output_dir}/results.txt", 'w') as f:
    ...         f.write(data)
    
    Checking permissions:
    
    >>> @PathValidator(
    ...     arg_names=('executable',),
    ...     exists=True,
    ...     executable=True
    ... )
    ... def run_command(executable, *args):
    ...     # Validates that the executable exists and is executable
    ...     import subprocess
    ...     return subprocess.run([executable, *args])
    
    Notes
    -----
    - Path validation results are cached to improve performance when the same
      paths are validated multiple times.
    - The validator will check all specified conditions in sequence.
    - At runtime, paths can be provided as strings or pathlib.Path objects.
    - If both file_okay and dir_okay are False, a ValueError will be raised.
    
    See Also
    --------
    pathlib.Path : The standard library path manipulation class
    os.access : The underlying function used for permission checking
    """

    arg_names: tuple[str, ...]
    exists: bool = False
    readable: bool = False
    writable: bool = False
    executable: bool = False
    allowed_extensions: Optional[list[str]] = None
    file_okay: bool = True
    dir_okay: bool = True
    mkdirs: bool = False
    CACHE_SIZE: int = 128  # Maximum number of unique paths to cache

    def __post_init__(self):
        if not self.file_okay and not self.dir_okay:
            raise ValueError("At least one of `file_okay` or `dir_okay` must be True.")
        self.allowed_extensions = self.allowed_extensions or []
        self.arg_names = tuple(self.arg_names)

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
