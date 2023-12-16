from nbiatoolkit.auth import OAuth2
from nbiatoolkit.utils.nbia_endpoints import NBIA_ENDPOINTS
from nbiatoolkit.logger.logger import setup_logger
from nbiatoolkit.utils.md5 import validateMD5
from nbiatoolkit.dicomsort import DICOMSorter

import requests
from requests.exceptions import JSONDecodeError as JSONDecodeError
import io
import zipfile


class NBIAClient:
    """
    The NBIAClient class is a wrapper around the NBIA REST API. It provides
    methods to query the API and download series.
    
    The default authentication uses the guest account. If you have a username
    and password, you can pass them to the constructor.
    
    TODO:: Add docstring
    FIXME:: logger prints duplicate logs if you instantiate the class more
    than once
    """

    def __init__(self,
                    username: str = "nbia_guest",
                    password: str = "",
                    log_level: str = "INFO"
                    ) -> None:

        # Setup logger
        self.logger = setup_logger(
            name="NBIAClient",
            log_level=log_level,
            console_logging=True,
            log_file=None)

        # Setup OAuth2 client
        self.logger.debug(
            "Setting up OAuth2 client... with username %s", username)

        self._oauth2_client = OAuth2(username=username, password=password)
        self.api_headers = self._oauth2_client.getToken()

    # setter method to update logger with a new instance of setup_logger
    def setLogger(
        self,
        log_level: str = "INFO",
        console_logging: bool = False,
        log_file: str = None,
        log_dir: str = None,
        log_format: str = '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt: str = '%y-%m-%d %H:%M'
    ) -> bool:
        try:
            self.logger = setup_logger(
                name="NBIAClient",
                log_level=log_level,
                console_logging=console_logging,
                log_file=log_file,
                log_dir=log_dir,
                log_format=log_format,
                datefmt=datefmt
            )
            return True
        except Exception as e:
            self.logger.error("Error setting up logger: %s", e)
            return False

    def query_api(self, endpoint: NBIA_ENDPOINTS, params: dict = {}) -> dict:

        query_url = NBIA_ENDPOINTS.BASE_URL.value + endpoint.value

        self.logger.debug("Querying API endpoint: %s", query_url)
        try:
            response = requests.get(
                url=query_url,
                headers=self.api_headers,
                params=params
                )
            if response.headers.get('Content-Type') == 'application/json':
                response_data = response.json()
            else:
                # If response is binary data, return raw response
                response_data = response.content
        except JSONDecodeError as j:
            if (response.text == ""):
                self.logger.error("Response text is empty.")
                return response
            self.logger.error("Error parsing response as JSON: %s", j)
            self.logger.debug("Response: %s", response.text)
        except Exception as e:
            self.logger.error("Error querying API: %s", e)
            raise e

        return response_data

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

    def getBodyPartCounts(
        self, Collection: str = "", Modality: str = "") -> list:

        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.GET_BODY_PART_PATIENT_COUNT,
            params=PARAMS)

        bodyparts=[]
        for bodypart in response:
            bodyparts.append({
                "BodyPartExamined": bodypart["criteria"],
                "Count": bodypart["count"]})
        return bodyparts

    def getPatients(self, Collection: str, Modality: str) -> list:
        assert Collection is not None
        assert Modality is not None


        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.GET_PATIENT_BY_COLLECTION_AND_MODALITY,
            params=PARAMS)

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

        PARAMS = dict()

        for key, value in locals().items():
            if (value != "") and (key != "self"):
                PARAMS[key] = value


        response = self.query_api(
            endpoint = NBIA_ENDPOINTS.GET_SERIES,
            params = PARAMS)

        return response


    def downloadSeries(
        self,
        SeriesInstanceUID: str,
        downloadDir: str = "./NBIA-Download",
        filePattern: str = '%PatientName/%StudyDescription-%StudyDate/%SeriesNumber-%SeriesDescription-%SeriesInstanceUID/%InstanceNumber.dcm',
        overwrite: bool = False
        ) -> bool:

        # create temporary directory
        from tempfile import TemporaryDirectory

        params = dict()
        params["SeriesInstanceUID"] = SeriesInstanceUID

        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.DOWNLOAD_SERIES,
            params=params)

        if not isinstance(response, bytes):
            # Handle the case where the expected binary data is not received
            # Log error or raise an exception
            return False

        file = zipfile.ZipFile(io.BytesIO(response))

        with TemporaryDirectory() as tempDir:
            file.extractall(path=tempDir)
            if not validateMD5(seriesDir=tempDir) and not overwrite:
                self.logger.error("MD5 validation failed. Exiting...")
                return False

            # Create an instance of DICOMSorter with the desired target pattern
            sorter = DICOMSorter(
                sourceDir=tempDir,
                destinationDir=downloadDir,
                targetPattern=filePattern,
                truncateUID=True,
                sanitizeFilename=True
                )

            sorter.sortDICOMFiles(option="move", overwrite=overwrite)

        return True

    # parsePARAMS is a helper function that takes a locals() dict and returns
    # a dict with only the non-empty values
    def parsePARAMS(self, params: dict) -> dict:
        self.logger.debug("Parsing params: %s", params)
        PARAMS = dict()
        for key, value in params.items():
            if (value != "") and (key != "self"):
                PARAMS[key] = value
        return PARAMS


