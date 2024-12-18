from nbiatoolkit.auth import OAuth2
from nbiatoolkit.logging import logger


class NBIAClient:
	"""A client for interacting with the NBIA API.

	The NBIAClient class provides a high-level interface for querying the NBIA API and downloading DICOM series.

	Parameters
	----------
	    username (str, optional): The username for authentication. Defaults to "nbia_guest".
	    password (str, optional): The password for authentication. Defaults to an empty string.
	    log_level (str, optional): The log level for the logger. Defaults to "INFO".

	Attributes
	----------
	    OAuth_client (OAuth2): The OAuth2 client used for authentication.
	    headers (dict[str, str]): The API headers.
	    base_url (NBIA_ENDPOINTS): The base URL for API requests.
	    logger (Logger): The logger for logging client events.
	    return_type (str): The current return type for API responses.
	"""

	def __init__(
		self,
		username: str = "nbia_guest",
		password: str = "",
		log_level: str = "INFO",
	) -> None:
		logger.debug("Setting up OAuth2 client... with username %s", username)
		self._oauth2_client = OAuth2(username=username, password=password)
