from src.utils.nbia_endpoints import NBIA_ENDPOINTS
from src.auth import OAuth2
from src.utils.logger import setup_logger
import requests

class NBIAClient:
    def __init__(self, username: str = "nbia_guest", password: str = "") -> None:
        
        # Setup logger
        self.logger = setup_logger(name = "NBIAClient", console_logging=True, log_level='INFO')
        
        # Setup OAuth2 client
        self.logger.info("Setting up OAuth2 client...")
        self._oauth2_client = OAuth2(username=username, password=password)
        self.api_headers = {'Authorization': f'Bearer {self._oauth2_client.getToken()}'}
        
        
    def query_api(self, endpoint: NBIA_ENDPOINTS, params: dict = {}) -> dict:
        """
        Queries the NBIA API with the specified endpoint and parameters.

        Args:
            endpoint (NBIA_ENDPOINTS): The endpoint to query.
            params (dict, optional): The parameters to include in the query. Defaults to {}.

        Returns:
            dict: The JSON response from the API.
        """
        base_url = "https://services.cancerimagingarchive.net/nbia-api/services/"
        query_url = base_url + endpoint.value
        
        self.logger.info("Querying API endpoint: %s", query_url)
        response = requests.get(query_url, headers=self.api_headers).json()
        
        return response
        
    def getCollectionPatientCount(self) -> dict:
        return self.query_api(NBIA_ENDPOINTS.GET_COLLECTION_PATIENT_COUNT)
    
    def getCollections(self) -> dict:
        return self.query_api(NBIA_ENDPOINTS.GET_COLLECTIONS)
    
    def getBodyPartCounts(self, collection: str = "", modality: str = "") -> dict:
        PARAMS = {}
        if collection:
            PARAMS["Collection"] = collection
        if modality:
            PARAMS["Modality"] = modality
        
        return self.query_api(endpoint = NBIA_ENDPOINTS.GET_BODY_PART_PATIENT_COUNT, params = PARAMS)
