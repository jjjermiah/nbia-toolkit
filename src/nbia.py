from src.utils.nbia_endpoints import NBIA_ENDPOINTS
from src.auth import OAuth2
from src.utils.logger import setup_logger
import requests
from requests.exceptions import JSONDecodeError as JSONDecodeError
class NBIAClient:
    def __init__(self, 
                 username: str = "nbia_guest", 
                 password: str = "",
                 log_level: str = "INFO"
                 ) -> None:
        
        # Setup logger
        self.logger = setup_logger(
            name = "NBIAClient", console_logging=True, log_level=log_level)
        
        # Setup OAuth2 client
        self.logger.info("Setting up OAuth2 client... with username %s", username)
        self._oauth2_client = OAuth2(username=username, password=password)
        self.api_headers = self._oauth2_client.getToken()
        
    def query_api(self, endpoint: NBIA_ENDPOINTS, params: dict = {}) -> dict:
        base_url = "https://services.cancerimagingarchive.net/nbia-api/services/"
        query_url = base_url + endpoint.value
        
        self.logger.info("Querying API endpoint: %s", query_url)
        self.logger.debug("API headers: %s", (self._createDebugURL(endpoint, params)))
        
        try:
            response = requests.get(
                url=query_url, 
                headers=self.api_headers,
                params=params
                )
            response = response.json()
        except JSONDecodeError as j:
            if (response.text==""):
                self.logger.error("Response text is empty.")
                return response
            self.logger.error("Error parsing response as JSON: %s", j)
            self.logger.debug("Response: %s", response.text)
        except Exception as e:
            self.logger.error("Error querying API: %s", e)
            raise e
        
        
        return response
    
    def _createDebugURL(self, endpoint, params):
        auth = "'Authorization:" + self.api_headers["Authorization"] + "' -k "
        base_url = "'https://services.cancerimagingarchive.net/nbia-api/services/"
        query_url = auth + base_url + endpoint.value
        debug_url = query_url + "?"
        for key, value in params.items():
            debug_url += f"{key}={value}&"
        debug_url = debug_url[:-1] + "'"
        return debug_url
    
    def getCollections(self) -> list:
        response = self.query_api(NBIA_ENDPOINTS.GET_COLLECTIONS)
        collections = []
        for collection in response:
            collections.append(collection["Collection"])
        return collections

    def getCollectionPatientCount(self) -> list:
        response = self.query_api(NBIA_ENDPOINTS.GET_COLLECTION_PATIENT_COUNT)
        patientCount = []
        for collection in response:
            patientCount.append({
                "Collection": collection["criteria"], 
                "PatientCount": collection["count"]})
            
        return patientCount
    
    def getBodyPartCounts(self, collection: str = "", modality: str = "") -> list:
        PARAMS = {}
        if collection:
            PARAMS["Collection"] = collection
        if modality:
            PARAMS["Modality"] = modality
        response =  self.query_api(
            endpoint = NBIA_ENDPOINTS.GET_BODY_PART_PATIENT_COUNT, 
            params = PARAMS)
        
        bodyparts=[]
        for bodypart in response:
            bodyparts.append({
                "BodyPartExamined": bodypart["criteria"], 
                "Count": bodypart["count"]})
        return bodyparts

    def getPatients(self, collection: str, modality: str) -> list:
        assert collection is not None
        assert modality is not None
        
        PARAMS = {"Collection": collection,"Modality": modality}
        response = self.query_api(
            endpoint = NBIA_ENDPOINTS.GET_PATIENT_BY_COLLECTION_AND_MODALITY, 
            params = PARAMS)
        patientList = [_["PatientId"] for _ in response]
        return patientList

