from __future__ import annotations

import asyncio
from io import BytesIO
import re
from dataclasses import dataclass, field

import pandas as pd
from rich.progress import (
    BarColumn,
    SpinnerColumn,
    TimeElapsedColumn,
)

from nbiatoolkit import (
    NBIA_BASE_URLS,
    NBIA_ENDPOINT,
    OAuth2,
    RichProgressBar,
    logger,
)
from nbiatoolkit.base_client import BaseClient
from nbiatoolkit.settings import Settings


@dataclass(unsafe_hash=True)
class NBIAClient(BaseClient):
    username: str = "nbia_guest"
    password: str = ""
    disable_progress_bar: bool = False
    log_level: str = "INFO"
    base_url: str = NBIA_BASE_URLS.NBIA.value

    max_concurrent_requests: int | None = None
    max_attempts: int | None = None
    wait_multiplier: float | None = None
    min_wait: int | None = None
    max_wait: int | None = None
    timeout_seconds: float | None = None

    OAuth_client: OAuth2 = field(init=False)
    progress_bar: RichProgressBar = field(init=False)

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
    ) -> NBIAClient:
        """Create an NBIAClient instance using settings."""
        # by default use the NBIA base URL
        return cls(
            username=settings.NBIA_USERNAME,
            password=settings.NBIA_PASSWORD,
            log_level=settings.log_level,
            **settings.api.model_dump(),
        )

    def __post_init__(self) -> None:
        # initialize ClientSession and Semaphore in BaseClient
        super().__init__(
            base_url=self.base_url,
            max_concurrent_requests=self.max_concurrent_requests,
            max_attempts=self.max_attempts,
            wait_multiplier=self.wait_multiplier,
            min_wait=self.min_wait,
            max_wait=self.max_wait,
            timeout_seconds=self.timeout_seconds,
        )
        self.OAuth_client = OAuth2(username=self.username, password=self.password)
        self.progress_bar = RichProgressBar(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            SpinnerColumn(),
            "Time elapsed:",
            TimeElapsedColumn(),
            transient=True,
            disable=self.disable_progress_bar,
        )
        logger.setLevel(self.log_level)

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.OAuth_client.access_token}",
            "Content-Type": "application/json",
        }

    ########## Collection Methods ###########
    #########################################

    async def _getCollections(self) -> list[dict]:
        return await self.query_json(
            NBIA_ENDPOINT.GET_COLLECTIONS.value,
        )

    def getCollections(self) -> list[dict]:
        return asyncio.run(self._getCollections())

    ######### Patient Methods ###########
    #####################################

    async def _getPatients(self, params: dict | list[dict]) -> list[dict]:
        if isinstance(params, list):
            logger.info(
                f"Starting {len(params)} patients requests"
                f" with max concurrency of {self.max_concurrent_requests}"
            )

            # Create tasks but control their execution through gather
            tasks = [
                self.query_json(NBIA_ENDPOINT.GET_PATIENTS.value, param)
                for param in params
            ]
            responses = await asyncio.gather(*tasks)

            # flatten the list of responses
            patient_list = [item for sublist in responses for item in sublist]
            logger.info(f"Completed {len(params)} patients requests")
            return patient_list
        # For a single parameter set
        return await self.query_json(
            NBIA_ENDPOINT.GET_PATIENTS.value,
            params=params,
        )

    def getPatients(self, params: dict | list[dict]) -> list[dict]:
        """Get patient metadata from NBIA."""
        return asyncio.run(self._getPatients(params))

    #### Study Methods ###########
    ###############################

    async def _getStudies(self, params: dict | list[dict]) -> list[dict]:
        """Fetch study data, supporting single or multiple parameter sets."""
        if isinstance(params, list):
            logger.info(
                f"Starting {len(params)} study requests"
                f" with max concurrency of {self.max_concurrent_requests}"
            )

            # Create tasks but control their execution through gather
            tasks = [
                self.query_json(NBIA_ENDPOINT.GET_STUDIES.value, param)
                for param in params
            ]
            responses = await asyncio.gather(*tasks)

            # flatten the list of responses
            study_list = [item for sublist in responses for item in sublist]
            logger.info(f"Completed {len(params)} study requests")
            return study_list
        # For a single parameter set
        return await self.query_json(
            NBIA_ENDPOINT.GET_STUDIES.value,
            params=params,
        )

    def getStudies(self, params: dict | list[dict]) -> list[dict]:
        """Get study metadata from NBIA."""
        return asyncio.run(self._getStudies(params))

    #### Series Methods ###########
    ###############################

    async def _getSeries(self, params: dict | list[dict]) -> list[dict]:
        """Fetch series data, supporting single or multiple parameter sets."""
        if isinstance(params, list):
            logger.info(
                f"Starting {len(params)} series requests" +
                f" with max concurrency of {self.max_concurrent_requests}"
            )

            # Create tasks but control their execution through gather
            tasks = [
                self.query_json(NBIA_ENDPOINT.GET_SERIES.value, param)
                for param in params
            ]
            responses = await asyncio.gather(*tasks)

            # flatten the list of responses
            series_list = [item for sublist in responses for item in sublist]
            logger.info(f"Completed {len(params)} series requests")
            return series_list

        # For a single parameter set
        return await self.query_json(
            NBIA_ENDPOINT.GET_SERIES.value,
            params=params,
        )

    def getSeries(self, params: dict | list[dict]) -> list[dict]:
        """Get series metadata from NBIA."""
        return asyncio.run(self._getSeries(params))
    
    async def _getNewSeries(self, params: dict | list[dict]) -> list[dict]:
        """Fetch series data, supporting single or multiple parameter sets."""
        if isinstance(params, list):
            logger.info(
                f"Starting {len(params)} series requests"
                f" with max concurrency of {self.max_concurrent_requests}"
            )

            # Create tasks but control their execution through gather
            tasks = [
                self.query_json(NBIA_ENDPOINT.GET_UPDATED_SERIES.value, param)
                for param in params
            ]
            responses = await asyncio.gather(*tasks)

            # flatten the list of responses
            series_list = [item for sublist in responses for item in sublist]
            logger.info(f"Completed {len(params)} series requests")
            return series_list

        # For a single parameter set
        return await self.query_json(
            NBIA_ENDPOINT.GET_UPDATED_SERIES.value,
            params=params,
        )

    def getNewSeries(self, params: dict | list[dict]) -> list[dict]:
        """Get series metadata from NBIA."""
        return asyncio.run(self._getNewSeries(params))
    
    async def _getSeriesSize(self, params: dict | list[dict]) -> list[dict]:
        """Fetch series data, supporting single or multiple parameter sets."""
        if isinstance(params, list):
            logger.info(
                f"Starting {len(params)} series requests"
                f" with max concurrency of {self.max_concurrent_requests}"
            )

            # Create tasks but control their execution through gather
            tasks = [
                self.query_json(NBIA_ENDPOINT.GET_SERIES_SIZE.value, param)
                for param in params
            ]
            responses = await asyncio.gather(*tasks)

            # flatten the list of responses
            series_list = [item for sublist in responses for item in sublist]
            logger.info(f"Completed {len(params)} series requests")
            return series_list

        # For a single parameter set
        return await self.query_json(
            NBIA_ENDPOINT.GET_SERIES_SIZE.value,
            params=params,
        )

    def getSeriesSize(self, params: dict | list[dict]) -> list[dict]:
        """Get series metadata from NBIA."""
        return asyncio.run(self._getSeriesSize(params))

    async def _download_series(self, SeriesInstanceUID: str) -> BytesIO:
        """Download series metadata from NBIA."""
        endpoint = NBIA_ENDPOINT.DOWNLOAD_SERIES.value
        params = {"SeriesInstanceUID": SeriesInstanceUID}
        return await self.query_bytes(endpoint, params=params)

    def download_series(self, SeriesInstanceUID: str) -> BytesIO:
        """Download series metadata from NBIA."""
        return asyncio.run(self._download_series(SeriesInstanceUID))
    
    async def _download_single_image(self, SeriesInstanceUID: str, SOPInstanceUID: str) -> BytesIO:
        """Download series metadata from NBIA."""
        endpoint = NBIA_ENDPOINT.DOWNLOAD_IMAGE.value
        params = {"SeriesInstanceUID": SeriesInstanceUID, "SOPInstanceUID": SOPInstanceUID}
        return await self.query_bytes(endpoint, params=params)


    def download_single_image(self, SeriesInstanceUID: str, SOPInstanceUID: str) -> BytesIO:
        """Download single image from NBIAToolkit."""
        return asyncio.run(self._download_single_image(SeriesInstanceUID, SOPInstanceUID))

    async def _build_collection_database(
        self, params: dict | list[dict]
    ) -> list[tuple]:
        """Fetch raw data for collection database(s).

        Args:
            params: Dict or list of dicts with collection parameters

        Returns:
            List of tuples containing (patients, studies, series) data
        """
        results = []

        if isinstance(params, list):
            logger.info(
                f"Starting {len(params)} collection database requests "
                f" with max concurrency of {self.max_concurrent_requests}"
            )

            # Process each collection's data concurrently
            async def fetch_collection_data(param):
                patient_task = self._getPatients(params=param)
                study_task = self._getStudies(params=param)
                series_task = self._getSeries(params=param)

                # Run the tasks concurrently
                return await asyncio.gather(patient_task, study_task, series_task)

            # Create tasks for each collection
            tasks = [fetch_collection_data(param) for param in params]
            all_results = await asyncio.gather(*tasks)

            for result in all_results:
                patients, studies, series = result
                results.append((patients, studies, series))

            logger.info(f"Completed {len(params)} collection database requests")
        else:
            # Single collection case
            patient_task = self._getPatients(params=params)
            study_task = self._getStudies(params=params)
            series_task = self._getSeries(params=params)

            # Run the tasks concurrently
            patients, studies, series = await asyncio.gather(
                patient_task, study_task, series_task
            )
            results.append((patients, studies, series))

        return results

    def build_collection_database(
        self, params: dict | list[dict]
    ) -> pd.DataFrame | list[pd.DataFrame]:
        """Given Collection(s), build database(s) of all patients, studies, and series.

        Args:
            params: Dict with 'Collection' key or list of such dicts

        Returns:
            Single DataFrame or list of DataFrames containing merged collection data
        """
        # Get raw data
        raw_data_list = asyncio.run(self._build_collection_database(params))
        logger.debug(f"Done retrieving. Processing {len(raw_data_list)} collections")
        from nbiatoolkit.models.nbia_responses import (
            Patient,
            Series,
            Study,
        )

        def process_collection_data(patients, studies, series):
            """Process raw API data into a structured DataFrame."""
            df_series = Series.from_dicts(series).df
            df_studies = Study.from_dicts(studies).df
            df_patients = Patient.from_dicts(patients).df

            # Drop Collection, StudyDate, StudyDescription, and PatientID
            # from the series DataFrame
            df_series = df_series.drop(
                columns=["Collection", "StudyDate", "StudyDescription", "PatientID"]
            )

            # Merge the series DataFrame with the studies DataFrame
            # on StudyInstanceUID
            df_series = df_series.merge(
                df_studies,
                how="left",
                left_on="StudyInstanceUID",
                right_on="StudyInstanceUID",
            )

            # drop {'Collection', 'PatientBirthDate', 'PatientName', 'PatientSex'}
            # from the merged DataFrame
            df_series = df_series.drop(
                columns=["Collection", "PatientBirthDate", "PatientName", "PatientSex"]
            )

            # Merge the series DataFrame with the patients DataFrame
            # on PatientID
            df_series = df_series.merge(
                df_patients,
                how="left",
                left_on="PatientID",
                right_on="PatientId",
            )
            # drop 'PatientId' from the merged DataFrame
            df_series = df_series.drop(columns=["PatientId"])

            # column order
            cols = [
                "Collection",
                "Patient*",
                "Study*",
                "Modality",
                "Series*",
                # and then the rest of the columns
            ]

            def reorder_columns(df: pd.DataFrame, patterns: list[str]) -> pd.DataFrame:
                used_cols = set()
                ordered_cols = []

                for pat in patterns:
                    # Convert wildcard * to regex equivalent
                    regex = re.compile(f"^{pat.replace('*', '.*')}$")
                    matching = [
                        col
                        for col in df.columns
                        if regex.match(col) and col not in used_cols
                    ]
                    ordered_cols.extend(matching)
                    used_cols.update(matching)

                # Add remaining columns
                remaining = [col for col in df.columns if col not in used_cols]
                return df[ordered_cols + remaining]

                # order rows by PatientID, StudyInstanceUID, and Modality

            df_series = df_series.sort_values(
                ["PatientID", "StudyInstanceUID", "Modality"],
                ascending=[True, True, True],
                ignore_index=True,
            )

            return reorder_columns(df_series, cols)

        # Process each collection's data
        results = [process_collection_data(*data) for data in raw_data_list]

        # Return a single DataFrame for single input, list for multiple inputs
        return results[0] if len(results) == 1 else results

    async def _getSOPIDs(self, params: dict | list[dict]) -> dict[str, list[dict]]:
        """Fetch SOPInstanceUID data, supporting single or multiple parameter sets.
        Returns a mapping of SeriesInstanceUID to list of SOP Instance UIDs
        """
        if isinstance(params, list):
            logger.info(
                f"Starting {len(params)} SOPInstanceUID requests "
                f" with max concurrency of {self.max_concurrent_requests}"
            )

            # Create tasks but control their execution through gather
            tasks = [
                self.query_json(NBIA_ENDPOINT.GET_SOP_INSTANCE_UIDS.value, param)
                for param in params
            ]
            responses = await asyncio.gather(*tasks)

            #  map the series instance UIDs to the list of responses
            sop_map = {
                param["SeriesInstanceUID"]: [
                    item["SOPInstanceUID"] for item in sublist
                ]  # Flatten and map
                for param, sublist in zip(params, responses)
            }

            logger.info(f"Completed {len(params)} SOPInstanceUID requests")
            return sop_map

        # For a single parameter set
        result = await self.query_json(
            NBIA_ENDPOINT.GET_SOP_INSTANCE_UIDS.value,
            params=params,
        )
        return {params["SeriesInstanceUID"]: result}

    def getSOPIDs(self, params: dict | list[dict]) -> dict[str, list[dict]]:
        """Get SOPInstanceUID metadata from NBIA.
        Returns a mapping of SeriesInstanceUID to list of SOP Instance UIDs
        """
        return asyncio.run(self._getSOPIDs(params))


if __name__ == "__main__":
    from rich import print

    from nbiatoolkit import Settings

    settings = Settings()

    client = NBIAClient.from_settings(settings)

    s = "1.3.6.1.4.1.14519.5.2.1.6834.5010.263257070197787007872578860295"
    series_bytes = client.download_series(s)

    # save the series bytes to a file
    with open(f"series_{s}.zip", "wb") as f:
        f.write(series_bytes.getbuffer())

    # collections = client.getCollections()
    # all_dbs = client.build_collection_database(params=collections)

    # all_dbs = pd.concat(all_dbs, ignore_index=True)
    # all_dbs.to_csv('data/all_series.csv', index=False)

    # all_series = pd.read_csv('data/all_series.csv')
    # sop_map = client.getSOPIDs(
    # 	[{'SeriesInstanceUID': s} for s in all_series.SeriesInstanceUID.unique()[:100]]
    # )

    # all_series.SeriesInstanceUID.unique()

    # all_series = all_dbs.copy()

    # series = client.getSeries(params=collections[:1])
    # # params = {'Collection': 'Vestibular-Schwannoma-SEG'}
    # # series = client.getSeries(params=params)
    # # params = [
    # # 	{'Collection': 'Vestibular-Schwannoma-MC-RC'},
    # # 	{'Collection': 'Vestibular-Schwannoma-SEG'},
    # # ]
    # # series = client.getSeries(params=params)

    # from nbiatoolkit.models.nbia_responses import Series, SeriesList

    # s: SeriesList = Series.from_dicts(series)
