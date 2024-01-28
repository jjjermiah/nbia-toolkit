from .auth import OAuth2
from .utils.nbia_endpoints import NBIA_ENDPOINTS
from .logger.logger import setup_logger
from .utils.md5 import validateMD5
from .dicomsort import DICOMSorter

import requests
from requests.exceptions import JSONDecodeError as JSONDecodeError
from typing import Union
import io
import zipfile
from tqdm import tqdm


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
        self.log = setup_logger(
            name="NBIAClient", log_level=log_level, console_logging=True, log_file=None
        )

        # Setup OAuth2 client
        self.log.debug("Setting up OAuth2 client... with username %s", username)

        self._oauth2_client = OAuth2(username=username, password=password)
        self._api_headers = self._oauth2_client.getToken()

    @property
    def headers(self):
        return self._api_headers

    def query_api(self, endpoint: NBIA_ENDPOINTS, params: dict = {}) -> dict:
        query_url = NBIA_ENDPOINTS.BASE_URL.value + endpoint.value

        self.log.debug("Querying API endpoint: %s", query_url)
        try:
            response = requests.get(url=query_url, headers=self.headers, params=params)
            if response.headers.get("Content-Type") == "application/json":
                response_data = response.json()
            else:
                # If response is binary data, return raw response
                response_data = response.content
        except JSONDecodeError as j:
            if response.text == "":
                self.log.error("Response text is empty.")
                return response
            self.log.error("Error parsing response as JSON: %s", j)
            self.log.debug("Response: %s", response.text)
        except Exception as e:
            self.log.error("Error querying API: %s", e)
            raise e

        return response_data

    def getCollections(self, prefix: str = "") -> list[dict[str]]:
        response = self.query_api(NBIA_ENDPOINTS.GET_COLLECTIONS)
        collections = []
        for collection in response:
            name = collection["Collection"]
            if name.lower().startswith(prefix.lower()):
                collections.append(name)
        return collections

    # returns a list of dictionaries with the collection name and patient count
    def getCollectionPatientCount(self, prefix: str = "") -> list[dict[str, int]]:
        response = self.query_api(NBIA_ENDPOINTS.GET_COLLECTION_PATIENT_COUNT)
        patientCounts = []
        for collection in response:
            name = collection["criteria"]
            if name.lower().startswith(prefix.lower()):
                patientCounts.append(
                    {
                        "Collection": collection["criteria"],
                        "PatientCount": int(collection["count"]),
                    }
                )

        return patientCounts

    def getBodyPartCounts(self, Collection: str = "", Modality: str = "") -> list:
        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.GET_BODY_PART_PATIENT_COUNT, params=PARAMS
        )

        bodyparts = []
        for bodypart in response:
            bodyparts.append(
                {"BodyPartExamined": bodypart["criteria"], "Count": bodypart["count"]}
            )
        return bodyparts

    def getPatients(self, Collection: str, Modality: str) -> list:
        assert Collection is not None
        assert Modality is not None

        PARAMS = self.parsePARAMS(locals())

        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.GET_PATIENT_BY_COLLECTION_AND_MODALITY,
            params=PARAMS,
        )

        patientList = [_["PatientId"] for _ in response]
        return patientList

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
    ) -> list:
        PARAMS = dict()

        for key, value in locals().items():
            if (value != "") and (key != "self"):
                PARAMS[key] = value

        response = self.query_api(endpoint=NBIA_ENDPOINTS.GET_SERIES, params=PARAMS)

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

        self.log.debug("Downloading series: %s", SeriesInstanceUID)
        response = self.query_api(
            endpoint=NBIA_ENDPOINTS.DOWNLOAD_SERIES, params=params
        )

        if not isinstance(response, bytes):
            self.log.error(f"Expected binary data, but received: {type(response)}")
            return False

        file = zipfile.ZipFile(io.BytesIO(response))

        with TemporaryDirectory() as tempDir:
            file.extractall(path=tempDir)

            try:
                validateMD5(seriesDir=tempDir)
            except Exception as e:
                self.log.error("Error validating MD5 hash: %s", e)
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
                self.log.error(
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
        self.log.debug("Parsing params: %s", params)
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

    all = client.getCollections()
    pprint(all)

    sub = client.getCollections(prefix="aCrin")
    pprint(sub)
    # collections = client.getCollections()
    # pprint(collections[0:5])
    # seriesJSON = client.getSeries(Collection="4D-Lung")
    # # first get a list of the SeriesInstanceUIDs
    # seriesUIDS = [series['SeriesInstanceUID'] for series in seriesJSON]
    # pprint(seriesUIDS[0:5])

    # seriesUIDS = [
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.189721824525842725510380467695',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.336250251691987239290048605884',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.227929163446067537882961857921',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.925990093742075237571072608963',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.139116724721865252687455544825',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.364787732307640672278270360328',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.384197169742944248273003912317',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.149750833495190982103087204448',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.300347070051003027185063750283',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.317831614083862743715273480521',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.736089011729021729851027177073',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.133381852562664457904201355429',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.909088026336573109170906532418',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.953079890279542310843831057254',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.427052348021168186336245283790',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.295010883410722294053941635303',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.263257070197787007872578860295',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.672179203515231442641005032212',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.184961274239908956209701869504',
    #     '1.3.6.1.4.1.14519.5.2.1.6834.5010.797307942821711099898506950104']

    # downloadDir = "./data"
    # os.makedirs(downloadDir, exist_ok=True)

    # client.downloadSeries(
    #     seriesUIDS, downloadDir, overwrite=True, nParallel=8)

    # pprint(os.listdir(downloadDir))
