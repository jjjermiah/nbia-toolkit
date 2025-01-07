import asyncio
from dataclasses import dataclass, field
from io import BytesIO

import pydicom
from imgtools.modules import StructureSet  # type: ignore
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TimeElapsedColumn,
)

from nbiatoolkit import (
    NBIA_BASE_URLS,
    NBIA_ENDPOINT,
    OAuth2,
    RichProgressBar,
    console,
    logger,
)
from nbiatoolkit.retry_handler import RetryHandlerMixin
from nbiatoolkit.timer import timer


class FailedQueryError(Exception):
    pass


@dataclass(unsafe_hash=True)
class NBIAClient(RetryHandlerMixin):
    """A client for interacting with the NBIA API.

    The NBIAClient class provides a high-level interface for querying the NBIA API
    and downloading DICOM series.

    Parameters
    ----------
        username (str, optional): The username for authentication. Defaults to "nbia_guest".
        password (str, optional): The password for authentication. Defaults to an empty string.
        log_level (str, optional): The log level for the logger. Defaults to "INFO".

    Attributes
    ----------
        OAuth_client (OAuth2): The OAuth2 client used for authentication.
        headers (dict[str, str]): The API headers.
        base_url (NBIA_ENDPOINT): The base URL for API requests.
        logger (Logger): The logger for logging client events.
        return_type (str): The current return type for API responses.
        progress_bar (RichProgressBar): A reusable progress bar instance.

    Inherited Methods
    -----------------
        RetryHandlerMixin::async_get_request:
            Send an asynchronous GET request to the NBIA API.
    """

    username: str = "nbia_guest"
    password: str = ""
    log_level: str = "INFO"
    base_url: NBIA_BASE_URLS = NBIA_BASE_URLS.NBIA

    OAuth_client: OAuth2 = field(init=False)
    progress_bar: RichProgressBar = field(init=False)

    def __post_init__(self) -> None:
        logger.debug("Setting up OAuth2 client... with username %s", self.username)
        self.OAuth_client = OAuth2(username=self.username, password=self.password)
        logger.debug("Initializing reusable progress bar...")
        self.progress_bar = RichProgressBar(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            SpinnerColumn(),
            "Time elapsed:",
            TimeElapsedColumn(),
            transient=True,
        )  # Initialize a reusable progress bar

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.OAuth_client.access_token}",
            "Content-Type": "application/json",
        }

    async def _raw_query(
        self,
        endpoint: str | NBIA_ENDPOINT,
        params: dict | None = None,
    ) -> bytes:
        progress = self.progress_bar
        progress.start()
        task = progress.add_task(f"Querying {endpoint}...", total=None)
        url = self.base_url.value + endpoint
        params = params or {}
        hashable_params = frozenset(params.items())
        try:
            result = await self.async_get_request(
                url=url,
                headers=self.headers,
                params=dict(hashable_params),
            )
        except Exception as e:
            msg = f"Failed to query {endpoint}: {e}"
            msg += f"\nURL: {url}\nParams: {params}"
            logger.exception(msg)
            raise FailedQueryError(msg) from e
        else:
            if not result:
                msg = f"Failed to query {endpoint}: No content returned."
                logger.error(msg)
                raise FailedQueryError(msg)
        finally:
            progress.update(task, completed=1)
            progress.remove_task(task)
            progress.stop()
        return result

    async def query(
        self,
        endpoint: str | NBIA_ENDPOINT,
        params: dict | None = None,
    ) -> list[dict]:
        """Mainly for the metadata json responses"""
        result = await self._raw_query(endpoint=endpoint, params=params)

        parsed_result = await self.parse_json_response(
            response=result, encoding="utf-8"
        )

        if not parsed_result or not all(
            isinstance(r, dict) and r for r in parsed_result
        ):
            msg = f"Failed to parse JSON response for {endpoint}."
            msg += f"\n type(parsed_result): {type(parsed_result)}"
            logger.error(msg)
            raise FailedQueryError(msg)

        return parsed_result

    async def _downloadImage(
        self,
        params: dict,
    ) -> bytes:
        """Query the NBIA API."""
        endpoint = NBIA_ENDPOINT.DOWNLOAD_IMAGE
        return await self._raw_query(endpoint, params=params)

    def downloadImage(
        self,
        params: dict | list[dict],
    ) -> bytes | list[bytes]:
        if isinstance(params, list):
            return asyncio.run(self._download_multiple_images(params))
        else:
            return asyncio.run(self._downloadImage(params))

    async def _download_multiple_images(
        self,
        params: list[dict],
    ) -> list[bytes]:
        tasks = [self._downloadImage(p) for p in params]
        return await asyncio.gather(*tasks)

    async def _getSOPInstanceUIDs(self, SeriesInstanceUID: str | dict) -> dict:
        """Query the NBIA API."""
        endpoint = NBIA_ENDPOINT.GET_SOP_INSTANCE_UIDS

        match SeriesInstanceUID:
            case str():
                params = {"SeriesInstanceUID": SeriesInstanceUID}
            case dict() if "SeriesInstanceUID" in SeriesInstanceUID:
                params = SeriesInstanceUID
            case _:
                msg = (
                    "SeriesInstanceUID must be a string or a dictionary "
                    "containing the key 'SeriesInstanceUID'."
                )
                raise ValueError(msg)

        result = await self.query(
            endpoint=endpoint.value,
            params=params,
        )
        assert result and len(result) == 1, f"Unexpected result: {result}"

        return {
            "SeriesInstanceUID": SeriesInstanceUID,
            **result[0],
        }

    def getSOPInstanceUIDs(
        self, SeriesInstanceUID: list[str] | str
    ) -> dict | list[dict]:
        if isinstance(SeriesInstanceUID, list):
            return asyncio.run(self._get_multiple_SOPInstanceUIDs(SeriesInstanceUID))
        else:
            return asyncio.run(self._getSOPInstanceUIDs(SeriesInstanceUID))

    async def _get_multiple_SOPInstanceUIDs(
        self, SeriesInstanceUIDs: list[str]
    ) -> list[dict]:
        tasks = [self._getSOPInstanceUIDs(uid) for uid in SeriesInstanceUIDs]
        return await asyncio.gather(*tasks)

    async def _getSeries(
        self,
        params: dict,
    ) -> list:
        """Query the NBIA API."""
        endpoint = NBIA_ENDPOINT.GET_SERIES
        return await self.query(endpoint, params=params)

    def getSeries(
        self,
        params: dict,
    ) -> list:
        return asyncio.run(self._getSeries(params))


@timer
def get_single_image_per_series(
    collection: str,
    modality: str,
    num_series: int,
    client: NBIAClient | None = None,
) -> list[pydicom.dataset.FileDataset]:
    client = client or NBIAClient()

    series = client.getSeries(params={"Modality": modality, "Collection": collection})

    series = series[:num_series]
    result = client.getSOPInstanceUIDs([s["SeriesInstanceUID"] for s in series])

    match result:
        case list():
            sops = result
        case dict():
            sops = [result]
        case _:
            msg = "Unexpected result type."
            raise ValueError(msg)
    raw_images = client.downloadImage(sops)

    # Ensure raw_images is a list of bytes
    if isinstance(raw_images, bytes):
        raw_images = [raw_images]

    # convert the bytes to pydicom objects
    dcm_images = [
        # pydicom.dcmread(BytesIO(img), specific_tags=["Modality"]) for img in raw_images
        StructureSet.from_dicom_rtstruct(BytesIO(img))
        for img in raw_images
    ]

    filtered = [
        dcm for dcm in dcm_images if dcm.search_roi("Heart.*")
    ]

    return filtered


if __name__ == "__main__":
    client = NBIAClient()

    result = get_single_image_per_series(
        collection="NSCLC-Radiomics",
        modality="RTSTRUCT",
        num_series=5,
        client=client,
    )
    console.print(result)
