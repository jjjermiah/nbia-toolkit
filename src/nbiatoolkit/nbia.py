from .auth import OAuth2
from .logger.logger import setup_logger
from logging import Logger
from .utils import (
    NBIA_ENDPOINTS,
    validateMD5,
    clean_html,
    convertMillis,
    convertDateFormat,
)
from .dicomsort import DICOMSorter

import requests
from requests.exceptions import JSONDecodeError as JSONDecodeError
from typing import Union
import io
import zipfile

import os
from datetime import datetime

# set __version__ variable
__version__ = "0.29.2"


class NBIAClient:
    """
    The NBIAClient class is a wrapper around the NBIA REST API. It provides
    methods to query the API and download series.

    The default authentication uses the guest account. If you have a username
    and password, you can pass them to the constructor.

    TODO:: Add docstring
    """

    def __init__(
        self, username: str = "nbia_guest", password: str = "", log_level: str = "INFO"
    ) -> None:
        # Setup logger
        self._log: Logger = setup_logger(
            name="NBIAClient", log_level=log_level, console_logging=True, log_file=None
        )

        # Setup OAuth2 client
        self._log.debug("Setting up OAuth2 client... with username %s", username)
        self._oauth2_client = OAuth2(username=username, password=password)

        try:
            self._api_headers = {
                "Authorization": f"Bearer {self._oauth2_client.access_token}",
                "Content-Type": "application/json",
            }
        except Exception as e:
            self._log.error("Error retrieving access token: %s", e)
            self._api_headers = None
            raise e
        self._base_url: NBIA_ENDPOINTS = NBIA_ENDPOINTS.BASE_URL

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._oauth2_client.logout()

    @property
    def OAuth_client(self) -> OAuth2:
        return self._oauth2_client

    @property
    def headers(self):
        return self._api_headers

    # create a setter for the base_url in case user want to use NLST
    @property
    def base_url(self) -> NBIA_ENDPOINTS:
        return self._base_url

    @base_url.setter
    def base_url(self, nbia_url: NBIA_ENDPOINTS) -> None:
        self._base_url = nbia_url

    @property
    def logger(self) -> Logger:
        return self._log

    @logger.setter
    def logger(self, logger: Logger) -> None:
        self._log = logger

    def query_api(
        self, endpoint: NBIA_ENDPOINTS, params: dict = {}
    ) -> Union[dict | list, bytes, None]:
        # query_url = NBIA_ENDPOINTS.BASE_URL.value + endpoint.value
        query_url: str = self._base_url.value + endpoint.value

        self._log.debug("Querying API endpoint: %s", query_url)
        self._log.debug("Query parameters: %s", params)

        response: requests.Response | None = None

        try:
            response = requests.get(url=query_url, headers=self.headers, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            if response.headers.get("Content-Type") == "application/json":
                return response.json()
            else:
                return response.content
        except JSONDecodeError as j:
            self._log.error("Error parsing response as JSON: %s", j)
            if response is not None:
                self._log.debug("Response: %s", response.text)
                if not response.text.strip():
                    self._log.error("Response text is empty.")
            raise j
        except requests.exceptions.HTTPError as http_err:
            self._log.error("HTTP error occurred: %s", http_err)
            if response is None:
                self._log.error("Response is None")
                raise http_err
            if response.status_code != 200:
                self._log.error(
                    "Error querying API: %s %s", response.status_code, response.reason
                )
                raise http_err
        except requests.exceptions.RequestException as e:
            self._log.error("Error querying API: %s", e)
            raise e
        except Exception as e:
            self._log.error("Error querying API: %s", e)
            raise e

    def getCollections(self, prefix: str = "") -> Union[list[str], None]:
        response = self.query_api(NBIA_ENDPOINTS.GET_COLLECTIONS)

        if not isinstance(response, list):
            self._log.error("Expected list, but received: %s", type(response))
            return None

        collections = []
        for collection in response:
            name = collection["Collection"]
            if name.lower().startswith(prefix.lower()):
                collections.append(name)
        return collections

    def getCollectionDescriptions(
        self, collectionName: str
    ) -> Union[list[dict[str, str]], None]:
        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(NBIA_ENDPOINTS.GET_COLLECTION_DESCRIPTIONS, PARAMS)

        if len(response) == 0:
            raise ValueError(
                "The response from the API is empty. Please check the collection name."
            )

        api_response = response[0]
        if not isinstance(api_response, dict):
            raise ValueError("The response from the API is not a dictionary")

        returnVal: dict[str, str] = {
            "collectionName": api_response["collectionName"],
            "description": clean_html(api_response["description"]),
            "descriptionURI": api_response["descriptionURI"],
            "lastUpdated": convertMillis(
                millis=int(api_response["collectionDescTimestamp"])
            ),
        }

        return [returnVal]

    def getModalityValues(
        self, Collection: str = "", BodyPartExamined: str = ""
    ) -> Union[list[str], None]:
        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.GET_MODALITY_VALUES, params=PARAMS
        )

        if not isinstance(response, list):
            self._log.error("Expected list, but received: %s", type(response))
            return None

        modalities = []
        for modality in response:
            modalities.append(modality["Modality"])
        return modalities

    def getPatients(self, Collection: str = "") -> Union[list[dict[str, str]], None]:
        assert isinstance(Collection, str), "Collection must be a string"

        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(endpoint=NBIA_ENDPOINTS.GET_PATIENTS, params=PARAMS)
        if not isinstance(response, list):
            self._log.error("Expected list, but received: %s", type(response))
            return None

        patientList = []
        for patient in response:
            assert isinstance(patient, dict), "Expected dict, but received: %s" % type(
                patient
            )
            assert "PatientId" in patient, "PatientId not in patient dict"
            assert isinstance(
                patient["PatientId"], str
            ), "PatientId must be a string, but received: %s" % type(
                patient["PatientId"]
            )

            patientList.append(patient)

        return patientList

    def getNewPatients(
        self,
        Collection: str,
        Date: Union[str, datetime],
    ) -> Union[list[dict[str, str]], None]:
        assert Collection is not None
        assert Date is not None

        # convert date to %Y/%m/%d format
        Date = convertDateFormat(input_date=Date, format="%Y/%m/%d")

        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.GET_NEW_PATIENTS_IN_COLLECTION, params=PARAMS
        )
        assert isinstance(response, list), "Expected list, but received: %s" % type(
            response
        )

        patientList = []
        for patient in response:
            assert isinstance(patient, dict), "Expected dict, but received: %s" % type(
                patient
            )
            assert "PatientId" in patient, "PatientId not in patient dict"
            assert isinstance(
                patient["PatientId"], str
            ), "PatientId must be a string, but received: %s" % type(
                patient["PatientId"]
            )

            patientList.append(patient)

        return patientList

    def getPatientsByCollectionAndModality(
        self, Collection: str, Modality: str
    ) -> Union[list[str], None]:
        assert Collection is not None
        assert Modality is not None

        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.GET_PATIENT_BY_COLLECTION_AND_MODALITY,
            params=PARAMS,
        )
        if not isinstance(response, list):
            self._log.error("Expected list, but received: %s", type(response))
            return None

        patientList = [_["PatientId"] for _ in response]
        return patientList

    # returns a list of dictionaries with the collection name and patient count
    def getCollectionPatientCount(
        self, prefix: str = ""
    ) -> Union[list[dict[str, int]], None]:
        response = self.query_api(NBIA_ENDPOINTS.GET_COLLECTION_PATIENT_COUNT)

        if not isinstance(response, list):
            self._log.error("Expected list, but received: %s", type(response))
            return None

        patientCounts = []
        for collection in response:
            CollectionName = collection["criteria"]
            if CollectionName.lower().startswith(prefix.lower()):
                patientCounts.append(
                    {
                        "Collection": CollectionName,
                        "PatientCount": int(collection["count"]),
                    }
                )
        return patientCounts

    def getBodyPartCounts(
        self, Collection: str = "", Modality: str = ""
    ) -> Union[list[dict[str, int]], None]:
        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.GET_BODY_PART_PATIENT_COUNT, params=PARAMS
        )

        if not isinstance(response, list):
            self._log.error("Expected list, but received: %s", type(response))
            return None

        bodyparts = []
        for bodypart in response:
            bodyparts.append(
                {
                    "BodyPartExamined": bodypart["criteria"],
                    "Count": int(bodypart["count"]),
                }
            )
        return bodyparts

    def getStudies(
        self, Collection: str, PatientID: str = "", StudyInstanceUID: str = ""
    ) -> Union[list[dict[str, str]], None]:
        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(endpoint=NBIA_ENDPOINTS.GET_STUDIES, params=PARAMS)

        if not isinstance(response, list):
            self._log.error("Expected list, but received: %s", type(response))
            return None

        return response

    def getSeries(
        self,
        Collection: str = "",
        PatientID: str = "",
        StudyInstanceUID: str = "",
        Modality: str = "",
        SeriesInstanceUID: str = "",
        BodyPartExamined: str = "",
        ManufacturerModelName: str = "",
        Manufacturer: str = "",
    ) -> Union[list[dict[str, str]], None]:
        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(endpoint=NBIA_ENDPOINTS.GET_SERIES, params=PARAMS)

        if not isinstance(response, list):
            self._log.error("Expected list, but received: %s", type(response))
            return None

        return response

    def getSeriesMetadata(
        self,
        SeriesInstanceUID: Union[str, list[str]],
    ) -> Union[list[dict], None]:
        assert isinstance(
            SeriesInstanceUID, (str, list)
        ), "SeriesInstanceUID must be a string or list of strings"

        if isinstance(SeriesInstanceUID, str):
            SeriesInstanceUID = [SeriesInstanceUID]

        metadata = []
        for seriesUID in SeriesInstanceUID:
            PARAMS = self.parsePARAMS({"SeriesInstanceUID": seriesUID})
            response = self.query_api(
                endpoint=NBIA_ENDPOINTS.GET_SERIES_METADATA, params=PARAMS
            )

            if not isinstance(response, list):
                self._log.error("Expected list, but received: %s", type(response))
                return None

            metadata.extend(response)

        return metadata

    def getNewSeries(
        self,
        Date: Union[str, datetime],
    ) -> Union[list[dict], None]:
        assert Date is not None and isinstance(
            Date, (str, datetime)
        ), "Date must be a string or datetime object"

        # for some reason this endpoint requires the date in %d/%m/%Y format
        fromDate = convertDateFormat(input_date=Date, format="%d/%m/%Y")
        PARAMS = self.parsePARAMS({"fromDate": fromDate})

        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.GET_UPDATED_SERIES, params=PARAMS
        )

        if not isinstance(response, list):
            self._log.error("Expected list, but received: %s", type(response))
            return None

        return response

    def getDICOMTags(
        self,
        SeriesInstanceUID: str,
    ) -> Union[list[dict], None]:
        assert SeriesInstanceUID is not None and isinstance(SeriesInstanceUID, str), \
            "SeriesInstanceUID must be a string"

        PARAMS = self.parsePARAMS({"SeriesUID": SeriesInstanceUID})

        response = self.query_api(endpoint=NBIA_ENDPOINTS.GET_DICOM_TAGS, params=PARAMS)

        if not isinstance(response, list):
            self._log.error("Expected list, but received: %s", type(response))
            return None

        return response


    def downloadSeries(
        self,
        SeriesInstanceUID: Union[str, list],
        downloadDir: str = "./NBIA-Download",
        filePattern: str = "%PatientName/%StudyDescription-%StudyDate/%SeriesNumber-%SeriesDescription-%SeriesInstanceUID/%InstanceNumber.dcm",
        overwrite: bool = False,
        nParallel: int = 1,
    ) -> bool:
        assert isinstance(
            SeriesInstanceUID, (str, list)
        ), "SeriesInstanceUID must be a string or list"
        assert isinstance(downloadDir, str), "downloadDir must be a string"
        assert isinstance(filePattern, str), "filePattern must be a string"
        assert isinstance(overwrite, bool), "overwrite must be a boolean"

        import concurrent.futures as cf
        from tqdm import tqdm

        if isinstance(SeriesInstanceUID, str):
            SeriesInstanceUID = [SeriesInstanceUID]

        with cf.ThreadPoolExecutor(max_workers=nParallel) as executor:
            futures = []

            try:
                os.makedirs(downloadDir)
            except FileExistsError:
                pass

            for seriesUID in SeriesInstanceUID:
                future = executor.submit(
                    self._downloadSingleSeries,
                    SeriesInstanceUID=seriesUID,
                    downloadDir=downloadDir,
                    filePattern=filePattern,
                    overwrite=overwrite,
                )
                futures.append(future)

            # Use tqdm to create a progress bar
            with tqdm(
                total=len(futures), desc=f"Downloading {len(futures)} series"
            ) as pbar:
                for future in cf.as_completed(futures):
                    pbar.update(1)

            return True

    # _downloadSingleSeries is a helper function that downloads a single series
    # to simplify the code in downloadSeries and also allow for parallel
    # downloads in the future
    def _downloadSingleSeries(
        self,
        SeriesInstanceUID: str,
        downloadDir: str,
        filePattern: str,
        overwrite: bool,
    ) -> bool:
        # create temporary directory
        from tempfile import TemporaryDirectory

        params = dict()
        params["SeriesInstanceUID"] = SeriesInstanceUID

        self._log.debug("Downloading series: %s", SeriesInstanceUID)
        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.DOWNLOAD_SERIES, params=params
        )

        if not isinstance(response, bytes):
            self._log.error(f"Expected binary data, but received: {type(response)}")
            return False

        file = zipfile.ZipFile(io.BytesIO(response))

        with TemporaryDirectory() as tempDir:
            file.extractall(path=tempDir)

            try:
                validateMD5(seriesDir=tempDir)
            except Exception as e:
                self._log.error("Error validating MD5 hash: %s", e)
                return False

            # Create an instance of DICOMSorter with the desired target pattern
            sorter = DICOMSorter(
                sourceDir=tempDir,
                destinationDir=downloadDir,
                targetPattern=filePattern,
                truncateUID=True,
                sanitizeFilename=True,
            )
            # sorter.sortDICOMFiles(option="move", overwrite=overwrite)
            if not sorter.sortDICOMFiles(option="move", overwrite=overwrite):
                self._log.error(
                    "Error sorting DICOM files for series %s\n \
                        failed files located at %s",
                    SeriesInstanceUID,
                    tempDir,
                )
                return False

        return True

    # parsePARAMS is a helper function that takes a locals() dict and returns
    # a dict with only the non-empty values
    def parsePARAMS(self, params: dict) -> dict:
        self._log.debug("Parsing params: %s", params)
        PARAMS = dict()
        for key, value in params.items():
            if (value != "") and (key != "self"):
                PARAMS[key] = value
        return PARAMS


# main
if __name__ == "__main__":
    from pprint import pprint
    import os

    client = NBIAClient(log_level="info")

    print(client.getStudies(Collection="TCGA-GBM"))
    # all = client.getCollections()
    # pprint(all)

    # sub = client.getCollections(prefix="aCrin")
    # pprint(sub)
