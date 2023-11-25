from nbiatoolkit.auth import OAuth2
from nbiatoolkit.utils.nbia_endpoints import NBIA_ENDPOINTS
from nbiatoolkit.utils.logger import setup_logger
from nbiatoolkit.utils.md5 import validateMD5
import requests
from requests.exceptions import JSONDecodeError as JSONDecodeError
import io, zipfile, os


class NBIAClient:
    """
    TODO:: Add docstring
    FIXME:: logger prints duplicate logs if you instantiate the class more than once
    """
        
    def __init__(self, 
                 username: str = "nbia_guest", 
                 password: str = "",
                 log_level: str = "INFO"
                 ) -> None:
        
        # Setup logger
        self.logger = setup_logger(
            name = "NBIAClient", 
            console_logging=True, 
            log_level=log_level,
            log_file = None)
        
        # Setup OAuth2 client
        self.logger.debug("Setting up OAuth2 client... with username %s", username)
        self._oauth2_client = OAuth2(username=username, password=password)
        self.api_headers = self._oauth2_client.getToken()
        
    def query_api(self, endpoint: NBIA_ENDPOINTS, params: dict = {}) -> dict:
        base_url = "https://services.cancerimagingarchive.net/nbia-api/services/"
        query_url = base_url + endpoint.value
        
        self.logger.debug("Querying API endpoint: %s", query_url)
        # self.logger.debug("API headers: %s", (self._createDebugURL(endpoint, params)))
        
        try:
            response = requests.get(
                url=query_url, 
                headers=self.api_headers,
                params=params
                )
             # Check if response is likely to be JSON
            if response.headers.get('Content-Type') == 'application/json':
                response_data = response.json()
            else:
                # If response is binary data, return raw response
                response_data = response.content
        except JSONDecodeError as j:
            if (response.text==""):
                self.logger.error("Response text is empty.")
                return response
            self.logger.error("Error parsing response as JSON: %s", j)
            self.logger.debug("Response: %s", response.text)
        except Exception as e:
            self.logger.error("Error querying API: %s", e)
            raise e
        
        return response_data
    
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

    def getSeries(self,
        Collection: str = "", 
        PatientID: str = "",
        StudyInstanceUID: str = "",
        Modality: str = "",
        SeriesInstanceUID: str = "",
        BodyPartExamined: str = "",
        ManufacturerModelName: str = "",
        Manufacturer: str = "",
        ) -> list:
        
        params = dict()
        
        for key, value in locals().items():
            if (value != "") and (key != "self"):
                params[key] = value
        
        
        response = self.query_api(
            endpoint = NBIA_ENDPOINTS.GET_SERIES,
            params = params)
        
        return response
        
    def downloadSeries(
        self, SeriesInstanceUID: str, downloadDir: str,
        ) -> bool:
        
        params = dict()
        params["SeriesInstanceUID"] = SeriesInstanceUID
        
        response = self.query_api(
            endpoint = NBIA_ENDPOINTS.DOWNLOAD_SERIES,
            params = params)
        
        if isinstance(response, bytes):
            file = zipfile.ZipFile(io.BytesIO(response))
            seriesDir = os.path.join(downloadDir, SeriesInstanceUID)
            file.extractall(path=seriesDir)
        
            validateMD5(seriesDir=seriesDir)
        else:
        # Handle the case where the expected binary data is not received
        # Log error or raise an exception
            pass

        return True
        
    
    
    
        