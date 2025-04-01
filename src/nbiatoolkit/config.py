"""This is an opinionated abstraction of platformdirs.

Whereas platformdirs on MacOS does not follow XDG, this module does.
"""
import os
import sys
from typing import TYPE_CHECKING
from nbiatoolkit import APP_AUTHOR, APP_NAME

if sys.platform == "win32":
    from platformdirs.windows import Windows as _Result
else:
    # elif sys.platform == "darwin":
    from platformdirs.unix import Unix as _Result

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Literal

if TYPE_CHECKING:
    # Work around mypy issue: https://github.com/python/mypy/issues/10962
    PlatformDirs = _Result
else:
    from platformdirs import _set_platform_dir_class
    PlatformDirs = _Result

dirs = PlatformDirs(appname=APP_NAME, appauthor=APP_AUTHOR)

