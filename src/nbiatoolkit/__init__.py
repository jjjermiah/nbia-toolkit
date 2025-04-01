# __init__.py
# Path: projects/nbia-toolkit/src/__init__.py

# this is the __init__.py file
# this file is run when the package is imported
# this file is used to import all the modules in the package
# this file is used to define the __all__ variable
__version__ = "0.1.0"
__author__ = "Jermiah Joseph"
PACKAGE_NAME = "NBIATOOLKIT"

APP_AUTHOR = __author__.replace(" ", "_").lower()
APP_NAME = PACKAGE_NAME.replace("-", "_").lower()

# import the modules
from .logging_config import logger, RichProgressBar, console  # noqa
from .auth import OAuth2
from .utils.nbia_endpoints import NBIA_BASE_URLS, NBIA_ENDPOINT
from .settings import Settings

__all__ = [
    "logger",
    "RichProgressBar",
    "console",
    "OAuth2",
    "NBIA_BASE_URLS",
    "NBIA_ENDPOINT",
    "Settings",
]

