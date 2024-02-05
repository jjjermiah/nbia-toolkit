import requests
import time
from typing import Union
from .utils import NBIA_ENDPOINTS

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
        self,
        username: str = "nbia_guest",
        password: str = "",
        client_id: str = "NBIA",
        base_url: Union[str, NBIA_ENDPOINTS] = NBIA_ENDPOINTS.BASE_URL,
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
        base_url : str or NBIA_ENDPOINTS, optional. Default is NBIA_ENDPOINTS.BASE_URL

        """
        self.client_id = client_id
        self.username = username
        self.password = password

        if isinstance(base_url, NBIA_ENDPOINTS):
            self.base_url = base_url.value
        else:
            self.base_url = base_url

        self._access_token = None
        self.expiry_time = None
        self.refresh_expiry = None
        self.refresh_token = ""  # Fix: Assign an empty string instead of None
        self.scope = None

    @property
    def access_token(self) -> str | None:
        # Check if access token is not set or it's expired
        if not self._access_token or self.is_token_expired():
            self.refresh_token_or_request_new()

        return self._access_token

    def is_token_expired(self) -> bool:
        # Check if the token expiration time is set and if it's expired
        return self.expiry_time is not None and time.time() > self.expiry_time

    def refresh_token_or_request_new(self) -> None:
        if self.refresh_token != "":
            self._refresh_access_token()
        else:
            self.request_new_access_token()

    def _refresh_access_token(self) -> None:
        assert self.refresh_token != "", "Refresh token is not set"

        # Prepare the request data
        data: dict[str, str] = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "grant_type": "refresh_token",
        }

        token_url: str = self.base_url + "oauth/token"

        response = requests.post(token_url, data=data)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise err
        else:
            token_data = response.json()
            self.set_token_data(token_data)



    def request_new_access_token(self):
        # Implement logic to request a new access token using client credentials
        # Set the new access token and update the expiration time
        # Example:
        # new_access_token, expires_in = your_token_request_logic()
        # self.access_token = new_access_token
        # self.token_expiration_time = time.time() + expires_in

        #     # Prepare the request data
        data: dict[str, str] = {
            "username": self.username,
            "password": self.password,
            "client_id": self.client_id,
            "grant_type": "password",
        }

        token_url: str = self.base_url + "oauth/token"

        response : requests.models.Response
        response = requests.post(token_url, data=data)

        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise err
        else:
            token_data = response.json()
            self.set_token_data(token_data)



    def set_token_data(self, token_data: dict):
        self._access_token = token_data["access_token"]
        self.expiry_time = time.time() + int(token_data.get("expires_in") or 0)
        self.refresh_token: str = token_data["refresh_token"]
        self.refresh_expiry = token_data.get("refresh_expires_in")
        self.scope = token_data.get("scope")

    @property
    def api_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",}


    @property
    def token_expiration_time(self):
        return self.expiry_time

    @property
    def refresh_expiration_time(self):
        return self.refresh_expiry

    @property
    def token_scope(self):
        return self.scope

    def __repr__(self):
        return f"OAuth2(username={self.username}, client_id={self.client_id})"

    def __str__(self):
        return f"OAuth2(username={self.username}, client_id={self.client_id})"

