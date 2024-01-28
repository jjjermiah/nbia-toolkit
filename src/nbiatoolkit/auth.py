import requests
import time
from typing import Union


class OAuth2:
    """
    OAuth2 class for handling authentication and access token retrieval.

    This class provides methods to authenticate with the NBIA API using OAuth2
    and retrieve the access token required for accessing the API.

    Defaults to using the NBIA Guest for accessing public collections.
    If you have a username and password which has been granted access
    to the collections tagged with "limited access" you can use those
    credentials to access those collections.


    Attributes
    ----------
    client_id : str
        The client ID for authentication.
    username : str
        The username for authentication.
    password : str
        The password for authentication.
    access_token : str or None
        The access token retrieved from the API.
    api_headers : dict or None
        The authentication headers containing the access token.
    expiry_time : str or None
        The expiry time of the access token.
    refresh_token : str or None
        The refresh token for obtaining a new access token.
    refresh_expiry : int or None
        The expiry time of the refresh token.
    scope : str or None
        The scope of the access token.

    Methods
    -------
    getToken()
        Authenticates with the API. Returns API headers containing the
        access token.

    Example Usage
    -------------
    >>> from nbiatoolkit.auth import OAuth2

    To use the NBIA Guest account:

    >>> oauth = OAuth2()

    To use a custom account:

    >>> oauth = OAuth2(username="my_username", password="my_password")

    Notes
    -----
    This class is mainly for developers looking to add functionality
    to the nbiatoolkit package. If you are a user looking to access the NBIA
    API, you can use the `NBIAClient` class without knowledge of this class.

    As there are many packages for handling OAuth2 authentication, this class
    was for myself to learn how OAuth2 works and to provide a simple way to
    authenticate with the NBIA API. If you have any suggestions for improving
    this class, please open an issue on the GitHub repository.
    """

    def __init__(
        self, username: str = "nbia_guest", password: str = "", client_id: str = "NBIA"
    ):
        """
        Initialize the OAuth2 class.


        Parameters
        ----------
        username : str, optional
            The username for authentication. Default is "nbia_guest".
        password : str, optional
            The password for authentication. Default is an empty string.
        client_id : str, optional
            The client ID for authentication. Default is "NBIA".
        """
        self.client_id = client_id
        self.username = username
        self.password = password
        self.access_token = None
        self.api_headers = None
        self.expiry_time = None
        self.refresh_token = None
        self.refresh_expiry = None
        self.scope = None

    def getToken(self) -> Union[dict, None]:
        """
        Retrieves the access token from the API.

        Returns
        -------
        api_headers : dict
            The authentication headers containing the access token.

        Example Usage
        -------------
        >>> from nbiatoolkit import OAuth2
        >>> oauth = OAuth2()
        >>> api_headers = oauth.getToken()

        >>> requests.get(url=query_url, headers=api_headers)
        """
        # Check if the access token is valid and not expired
        if self.access_token is not None:
            return None if self.access_token == None else self.access_token

        # Prepare the request data
        data = {
            "username": self.username,
            "password": self.password,
            "client_id": self.client_id,
            "grant_type": "password",
        }
        token_url = "https://services.cancerimagingarchive.net/nbia-api/oauth/token"

        response = requests.post(token_url, data=data)

        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()  # Raise an HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            self.access_token = None
            raise requests.exceptions.RequestException(
                f"Failed to get access token. Status code:\
                    {response.status_code}"
            ) from e
        else:
            # Code to execute if there is no exception
            token_data = response.json()
            self.access_token = token_data.get("access_token")

            self.api_headers = {"Authorization": f"Bearer {self.access_token}"}

            self.expiry_time = time.ctime(time.time() + token_data.get("expires_in"))
            self.refresh_token = token_data.get("refresh_token")
            self.refresh_expiry = token_data.get("refresh_expires_in")
            self.scope = token_data.get("scope")

            return self.api_headers

    @property
    def token(self):
        """
        Returns the access token.

        Returns
        -------
        access_token : str or None
            The access token retrieved from the API.
        """
        return self.access_token

    @property
    def headers(self):
        """
        Returns the API headers.

        Returns
        -------
        api_headers : dict or None
            The authentication headers containing the access token.
        """
        return self.api_headers
