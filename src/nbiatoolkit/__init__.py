## __init__.py
# Path: projects/nbia-toolkit/src/__init__.py

# this is the __init__.py file
# this file is run when the package is imported
# this file is used to import all the modules in the package
# this file is used to define the __all__ variable


# import the modules
from .nbia import NBIAClient, __version__, downloadSingleSeries
from .nbia_cli import version
from .auth import OAuth2
from .logger.logger import setup_logger
from .utils.nbia_endpoints import NBIA_ENDPOINTS

# define the __all__ variable
__all__ = [
    "NBIAClient",
    "OAuth2",
    "setup_logger",
    "NBIA_ENDPOINTS",
    "version",
    "__version__",
]
