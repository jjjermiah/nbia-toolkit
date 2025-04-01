import asyncio
import shutil
from dataclasses import dataclass, field
from typing import Any
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
    console,
    logger,
)
from nbiatoolkit.base_client import BaseClient


@dataclass(unsafe_hash=True)
class NBIAClient(BaseClient):
    username: str = "nbia_guest"
    password: str = ""
    disable_progress_bar: bool = False
    log_level: str = "INFO"
    base_url: str = NBIA_BASE_URLS.NBIA.value

    OAuth_client: OAuth2 = field(init=False)
    progress_bar: RichProgressBar = field(init=False)

    def __post_init__(self) -> None:
        super().__init__(base_url=self.base_url, log_level=self.log_level)
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



    #### Study Methods ###########
    ###############################


    #### Series Methods ###########
    ###############################

    async def _getSeries(self, params: dict | list[dict]) -> list[dict]:
        """Fetch series data, supporting single or multiple parameter sets."""
        description = "Fetching series..."
        if isinstance(params, list):
            # submit multiple requests at the same time
            tasks = [self.query_json(NBIA_ENDPOINT.GET_SERIES.value, param) for param in params]
            responses = await asyncio.gather(*tasks)

            # flatten the list of responses
            series_list = [item for sublist in responses for item in sublist]
            return series_list

        # For a single parameter set, use query_one
        return await self.query_json(
            NBIA_ENDPOINT.GET_SERIES.value,
            params=params,
        )

    def getSeries(self, params: dict | list[dict]) -> list[dict]:
        """Get series metadata from NBIA."""
        return asyncio.run(self._getSeries(params))


if __name__ == "__main__":
    from nbiatoolkit import Settings
    settings = Settings()

    client = NBIAClient(
        settings.NBIA_USERNAME,
        settings.NBIA_PASSWORD,
    )

    collections = client.getCollections()
    params = {'Collection': 'Vestibular-Schwannoma-SEG'}
    series = client.getSeries(params=params)
    params = [
        {'Collection': 'Vestibular-Schwannoma-MC-RC'},
        {'Collection': 'Vestibular-Schwannoma-SEG'}
    ]
    series = client.getSeries(params=params)

    series = client.getSeries(params=collections[-10:])
