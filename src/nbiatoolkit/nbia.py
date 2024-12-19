from nbiatoolkit import OAuth2, logger, RichProgressBar, NBIA_BASE_URLS, NBIA_ENDPOINTS
from dataclasses import dataclass, field
from nbiatoolkit.async_requests import async_query_api
from functools import lru_cache
from typing import Union
from rich.progress import Progress

@dataclass(unsafe_hash=True)
class NBIAClient:
	"""A client for interacting with the NBIA API.

	The NBIAClient class provides a high-level interface for querying the NBIA API and downloading DICOM series.

	Parameters
	----------
		username (str, optional): The username for authentication. Defaults to "nbia_guest".
		password (str, optional): The password for authentication. Defaults to an empty string.
		log_level (str, optional): The log level for the logger. Defaults to "INFO".

	Attributes
	----------
		OAuth_client (OAuth2): The OAuth2 client used for authentication.
		headers (dict[str, str]): The API headers.
		base_url (NBIA_ENDPOINTS): The base URL for API requests.
		logger (Logger): The logger for logging client events.
		return_type (str): The current return type for API responses.
	"""

	username: str = 'nbia_guest'
	password: str = ''
	log_level: str = 'INFO'
	base_url: NBIA_BASE_URLS = NBIA_BASE_URLS.NBIA
	OAuth_client: OAuth2 = field(init=False)

	def __post_init__(self) -> None:
		logger.debug('Setting up OAuth2 client... with username %s', self.username)
		self.OAuth_client = OAuth2(username=self.username, password=self.password)

	@property
	def headers(self) -> dict[str, str]:
		return {
			'Authorization': f'Bearer {self.OAuth_client.access_token}',
			'Content-Type': 'application/json',
		}

	async def query(self, progress: Progress, endpoint: NBIA_ENDPOINTS, params: Union[None, frozenset] = None) -> dict:
		"""Query the NBIA API."""
		hashable_params = frozenset(params.items()) if params else frozenset()
		task = progress.add_task(f'Querying {endpoint}...', total=None)

		try:
			result = await async_query_api(
				endpoint=endpoint.value,
				params=dict(hashable_params),  # Convert back to dict for the API call
				headers=self.headers,
				base_url=self.base_url.value,
			)
		finally:
			progress.update(task, completed=1)
			progress.remove_task(task)

		return result

	async def getInsanceUIDs(self, SeriesInstanceUID: str, progress: Progress) -> dict:
		"""Query the NBIA API."""
		endpoint = NBIA_ENDPOINTS.GET_SOP_INSTANCE_UIDS
		task = progress.add_task(f'Querying {endpoint}...', total=None)

		try:
			result = await async_query_api(
				endpoint=endpoint.value,
				params={'SeriesInstanceUID': SeriesInstanceUID},  # Convert back to dict for the API call
				headers=self.headers,
				base_url=self.base_url.value,
			)
		finally:
			progress.update(task, completed=1)
			progress.remove_task(task)

		return result



if __name__ == '__main__':
	from rich import print
	from rich.progress import SpinnerColumn, Progress, TimeElapsedColumn
	from nbiatoolkit.logging_config import console
	import asyncio
	import pandas as pd

	async def main():
		client = NBIAClient()

		with RichProgressBar(
			'[progress.description]{task.description}',
			SpinnerColumn(),
			'Time elapsed:',
			TimeElapsedColumn(),
			transient=True,
		) as progress:

			response_list = []
			# Define queries
			# response1 = client.query(progress, NBIA_ENDPOINTS.GET_COLLECTIONS)
			# response2 = client.query(progress, NBIA_ENDPOINTS.GET_MODALITY_VALUES)
			# response3 = client.query(progress, NBIA_ENDPOINTS.GET_MODALITY_PATIENT_COUNT)
			# response4 = client.query(progress, NBIA_ENDPOINTS.GET_PATIENTS)
			response_list.append(client.query(progress, NBIA_ENDPOINTS.GET_SERIES, params={'Modality': 'RTSTRUCT'}))
			responses = await asyncio.gather(*response_list)

			# Execute queries concurrently
			logger.info(f"Found {len(responses)} responses")
			for resp in responses:
				logger.info(f"Found {len(resp)} items")

			df = pd.DataFrame(responses[0])
			console.print(df)

			df.to_csv('Collections.csv', index=False)

			sop_tasks = []
			for s in df.itertuples():
				sop_tasks.append(client.getInsanceUIDs(s.SeriesInstanceUID, progress))

				if len(sop_tasks) == 50:
					break
			sop_responses = await asyncio.gather(*sop_tasks)

			print(sop_responses)
			# series_responses = [
			# 	client.query(
			# 		progress,
			# 		NBIA_ENDPOINTS.GET_SERIES,
			# 		params=col,
			# 	)
			# 	for col in responses[0][:25]
			# ]

			# series = await asyncio.gather(*series_responses)

			# for s in series:
			# 	print(f"Found {len(s)} series")

	asyncio.run(main())