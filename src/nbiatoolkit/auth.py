import requests
import time


class OAuth2:
    """
    OAuth2 class for handling authentication and access token retrieval.

    This class provides methods to authenticate with the NBIA API using OAuth2
    and retrieve the access token required for accessing the API.
    
    Defaults to using the NBIA Guest for accessing public collections.
    If you have a username and password which has been granted access
    to the collections tagged with "limited access" you can use those
    credentials to access those collections.
    
    NOTE::This class is mainly for developers looking to add functionality 
    to the nbiatoolkit package. If you are a user looking to access the NBIA 
    API, you can use the `NBIAClient` class without knowledge of this class.
    
    TODO::implement better access token handling
    TODO::implement better error handling
    TODO::implement refresh token functionality
    TODO::implement logout functionality
    TODO::implement encryption for username and password
    
    Attributes
    ----------
    client_id : str
        The client ID for authentication.
    username : str
        The username for authentication.
    password : str
        The password for authentication.
    access_token : str
        The access token retrieved from the API.

    Methods
    -------
    getToken()
        Authenticates with the API. Returns API headers containing the 
        access token.

    Example Usage
    -------------
    >>> from nbiatoolkit import OAuth2
    To use the NBIA Guest account:
    >>> oauth = OAuth2()
    To use a custom account:
    >>> oauth = OAuth2(username="my_username", password="my_password")

    """

    def __init__(self, username: str = "nbia_guest", password: str = "", client_id: str = "NBIA"):
        """
        Initialize the OAuth2 class.

        Parameters
        ----------
        client_id : str, optional
            The client ID for authentication. Default is "NBIA".
        username : str, optional
            The username for authentication. Default is "nbia_guest".
        password : str, optional
            The password for authentication. Default is an empty string.

        """
        self.client_id = client_id
        self.username = username
        self.password = password
        self.access_token = None

    def getToken(self):
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
            return 401 if self.access_token == 401 else self.access_token

        # Prepare the request data
        data = {
            'username': self.username,
            'password': self.password,
            'client_id': self.client_id,
            'grant_type': 'password'
        }
        token_url = 'https://services.cancerimagingarchive.net/nbia-api/oauth/token'

        response = requests.post(token_url, data=data)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error occurred: {e}")
            print(f"Failed to get access token. Status code: {response.status_code}")

            self.access_token = response.status_code
            return response.status_code

        token_data = response.json()
        self.access_token = token_data.get('access_token')

        self.api_headers = {
            'Authorization':f'Bearer {self.access_token}'
        }

        self.expiry_time = time.ctime(time.time() + token_data.get('expires_in'))
        self.refresh_token = token_data.get('refresh_token')
        self.refresh_expiry = token_data.get('refresh_expires_in')
        self.scope = token_data.get('scope')
        return self.api_headers
    
    # def logout(self):
    #     # Request for logout
    #     # curl -X -v -d "Authorization:Bearer YOUR_ACCESS_TOKEN" -k "https://services.cancerimagingarchive.net/nbia-api/logout"
        
        