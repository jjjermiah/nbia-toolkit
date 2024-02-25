import requests
import time
from typing import Union, Tuple
from .utils import NBIA_ENDPOINTS, NBIA_BASE_URLS
from cryptography.fernet import Fernet


def encrypt_credentials(key: bytes, username: str, password: str) -> Tuple[str, str]:
    """
    Encrypts the given username and password using the provided key.

    Args:
        key (bytes): The encryption key.
        username (str): The username to be encrypted.
        password (str): The password to be encrypted.

    Returns:
        Tuple[str, str]: A tuple containing the encrypted username and password.
    """
    cipher_suite = Fernet(key=key)
    encrypted_password = cipher_suite.encrypt(password.encode()).decode()
    encrypted_username = cipher_suite.encrypt(username.encode()).decode()
    return encrypted_username, encrypted_password


def decrypt_credentials(
    key: bytes, encrypted_username: str, encrypted_password: str
) -> tuple[str, str]:
    """
    Decrypts the encrypted username and password using the provided key.

    Args:
        key (bytes): The encryption key used to decrypt the credentials.
        encrypted_username (str): The encrypted username.
        encrypted_password (str): The encrypted password.

    Returns:
        tuple[str, str]: A tuple containing the decrypted username and password.
    """
    cipher_suite = Fernet(key=key)
    decrypted_username = cipher_suite.decrypt(encrypted_username.encode()).decode()
    decrypted_password = cipher_suite.decrypt(encrypted_password.encode()).decode()
    # return the decrypted client_id and username
    return decrypted_username, decrypted_password


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
        base_url: str | NBIA_BASE_URLS = NBIA_BASE_URLS.NBIA,
    ) -> None:
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
        base_url : str or NBIA_BASE_URLS, optional. Default is NBIA_BASE_URLS.NBIA

        """

        self.client_id = client_id

        self._fernet_key: bytes = Fernet.generate_key()
        self.username: str
        self.password: str
        self.username, self.password = encrypt_credentials(
            key=self.fernet_key, username=username, password=password
        )
        self.username, self.password = encrypt_credentials(
            key=self._fernet_key, username=username, password=password
        )

        if isinstance(base_url, NBIA_BASE_URLS):
            self.base_url = base_url.value
        else:
            self.base_url = base_url

        self._access_token = None
        self.expiry_time = None
        self.refresh_expiry = None
        self.refresh_token = ""  # Fix: Assign an empty string instead of None
        self.scope = None

    @property
    def fernet_key(self) -> bytes:
        return self._fernet_key

    def is_logged_out(self) -> bool:
        return (
            self._access_token == ""
            and self.username == ""
            and self.password == ""
            and self.client_id == ""
            and self.base_url == ""
        )

    @property
    def access_token(self) -> str | None:
        if self.is_logged_out():
            return None

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
        data: dict[str, str] = {
            "username": decrypt_credentials(
                key=self.fernet_key,
                encrypted_username=self.username,
                encrypted_password=self.password,
            )[0],
            "password": decrypt_credentials(
                key=self.fernet_key,
                encrypted_username=self.username,
                encrypted_password=self.password,
            )[1],
            "client_id": self.client_id,
            "grant_type": "password",
        }

        token_url: str = self.base_url + "oauth/token"

        response: requests.models.Response
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
            "Content-Type": "application/json",
        }

    @property
    def token_expiration_time(self):
        return self.expiry_time

    @property
    def refresh_expiration_time(self):
        return self.refresh_expiry

    @property
    def token_scope(self):
        return self.scope

    def __repr__(self) -> Union[str, None]:
        if self.username:
            return f"OAuth2(username={self.username}, client_id={self.client_id})"
        else:
            return ""

    def __str__(self):
        if self.username:
            return f"OAuth2(username={self.username}, client_id={self.client_id})"
        else:
            return ""

    def logout(self) -> None:
        """
        Logs out the user and revokes the access token.

        This method sends a request to the NBIA API to revoke the access token
        and logs out the user.

        Notes
        -----
        This method is not yet implemented in the NBIA API.
        """
        if not self.access_token:
            return None

        query_url = NBIA_BASE_URLS.LOGOUT_URL.value
        response = requests.get(query_url, headers=self.api_headers)
        response.raise_for_status()

        # set the entire object to None
        self.__dict__.clear()
        self.username = ""
        self.password = ""
        self.client_id = ""
        self.base_url = ""
        self._access_token = ""
        self.expiry_time = None
        self.refresh_expiry = None
        self.refresh_token = ""
        self.scope = None
        self._fernet_key = b""
        self = None
        return None
