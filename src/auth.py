import requests
import time
class OAuth2:
    def __init__(self,
                 client_id: str = "NBIA",
                 username: str = "nbia_guest",
                 password: str = ""):
        self.client_id = client_id
        self.username = username
        self.password = password
        self.access_token = None

    #username=nbia_guest&password=&client_id=NBIA&grant_type=password
    def getToken(self):
        # Check if the access token is valid and not expired
        if self.access_token is not None:
            return 401 if self.access_token == 401 else self.access_token

        # Prepare the request data4
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
            print(f"Failed to get access token. Status code: \
                {response.status_code}")
            
            self.access_token = response.status_code
            return response.status_code
        
        token_data = response.json()               
        self.access_token = token_data.get('access_token')                      

        self.api_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }                
        
        # TODO::implement refresh token functionality
        self.expiry_time = time.ctime(
            time.time() + token_data.get('expires_in') )            
        self.refresh_token = token_data.get('refresh_token')
        self.refresh_expiry = token_data.get('refresh_expires_in')
        self.scope = token_data.get('scope')
        return self.api_headers
                
    
    # def logout(self):
    #     # Request for logout
    #     # curl -X -v -d "Authorization:Bearer YOUR_ACCESS_TOKEN" -k "https://services.cancerimagingarchive.net/nbia-api/logout"
        
        