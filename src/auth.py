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
        self.api_headers = None

    #username=nbia_guest&password=&client_id=NBIA&grant_type=password
    def getToken(self):
        # Check if the access token is valid and not expired
        if self.access_token is not None and self.access_token != 401:
            return self.access_token
        elif self.access_token == 401:
            print("Failed to get access token. Status code: 401")
        else:
            # Prepare the request data4
            data = {
                'username': self.username,
                'password': self.password,
                'client_id': self.client_id,
                'grant_type': 'password'
            }
            token_url = 'https://services.cancerimagingarchive.net/nbia-api/oauth/token'
            # Make a POST request to the token endpoint
            response = requests.post(token_url, data=data) 
            # response.raise_for_status()
            
            # Check if the request was successful
            if response.status_code == 200:
                token_data = response.json()               
                self.access_token = token_data.get('access_token')                      
                # save access token to self for later use           
                # self.api_headers = {
                #     'Authorization': f'Bearer {self.access_token}',
                #     'Accept': 'application/json'
                # }                
                # TODO::implement refresh token functionality
                self.expiry_time = time.ctime(
                    time.time() + token_data.get('expires_in') )            
                self.refresh_token = token_data.get('refresh_token')
                self.refresh_expiry = token_data.get('refresh_expires_in')
                self.scope = token_data.get('scope')
                return self.access_token
            else:
                print(f"Failed to get access token. Status code: \
                    {response.status_code}")
                
                self.access_token = response.status_code
                return response.status_code
        
