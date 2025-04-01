from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

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
	username: str = 'nbia_guest'
	password: str = ''
	disable_progress_bar: bool = False
	log_level: str = 'INFO'
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
			'[progress.description]{task.description}',
			BarColumn(),
			'[progress.percentage]{task.percentage:>3.0f}%',
			SpinnerColumn(),
			'Time elapsed:',
			TimeElapsedColumn(),
			transient=True,
			disable=self.disable_progress_bar,
		)
		logger.setLevel(self.log_level)

	@property
	def headers(self) -> dict[str, str]:
		return {
			'Authorization': f'Bearer {self.OAuth_client.access_token}',
			'Content-Type': 'application/json',
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
		if isinstance(params, list):
			logger.info(
				f'Starting {len(params)} series requests'
				'with max concurrency of {self.max_concurrent_requests}'
			)

			# Create tasks but control their execution through gather
			tasks = [
				self.query_json(NBIA_ENDPOINT.GET_SERIES.value, param)
				for param in params
			]
			responses = await asyncio.gather(*tasks)

			# flatten the list of responses
			series_list = [item for sublist in responses for item in sublist]
			logger.info(f'Completed {len(params)} series requests')
			return series_list

		# For a single parameter set
		return await self.query_json(
			NBIA_ENDPOINT.GET_SERIES.value,
			params=params,
		)

	def getSeries(self, params: dict | list[dict]) -> list[dict]:
		"""Get series metadata from NBIA."""
		return asyncio.run(self._getSeries(params))


if __name__ == '__main__':
	from rich import print

	from nbiatoolkit import Settings

	settings = Settings()
	client = NBIAClient.from_settings(settings)

	collections = client.getCollections()
	series = client.getSeries(params=collections)
	# params = {'Collection': 'Vestibular-Schwannoma-SEG'}
	# series = client.getSeries(params=params)
	# params = [
	# 	{'Collection': 'Vestibular-Schwannoma-MC-RC'},
	# 	{'Collection': 'Vestibular-Schwannoma-SEG'},
	# ]
	# series = client.getSeries(params=params)

	from nbiatoolkit.models.nbia_responses import Series, SeriesList

	all_series: SeriesList = Series.from_dicts(series)
