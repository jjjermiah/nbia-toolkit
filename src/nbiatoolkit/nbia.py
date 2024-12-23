from dataclasses import dataclass, field
from typing import Union

from rich.progress import Progress

from nbiatoolkit import (
	NBIA_BASE_URLS,
	NBIA_ENDPOINTS,
	OAuth2,
	RichProgressBar,
	console,
	logger,
)
from nbiatoolkit.async_requests import async_query_api


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

	async def query(
		self,
		endpoint: NBIA_ENDPOINTS,
		params: Union[None, frozenset] = None,
		progress: Progress | None = None,
	) -> dict:
		"""Query the NBIA API."""
		if progress is None:
			progress = Progress()
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

	async def getInsanceUIDs(self, SeriesInstanceUID: str) -> dict:
		"""Query the NBIA API."""
		endpoint = NBIA_ENDPOINTS.GET_SOP_INSTANCE_UIDS

		result = await async_query_api(
			endpoint=endpoint.value,
			params={
				'SeriesInstanceUID': SeriesInstanceUID
			}, 
			headers=self.headers,
			base_url=self.base_url.value,
		)


		return result

if __name__ == '__main__':
	import asyncio

	import pandas as pd
	from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, BarColumn, TextColumn, ProgressColumn

	async def get_instance_uids_with_semaphore(client, SeriesInstanceUID, progress, semaphore, task):
		async with semaphore:
			result = await client.getInsanceUIDs(SeriesInstanceUID)
			progress.advance(task)
			return result
	
	async def get_image_with_semaphore(client, SeriesInstanceUID, SOPInstanceUID, progress, semaphore, task):
		async with semaphore:
			result = await client.getInsanceUIDs(SeriesInstanceUID, SOPInstanceUID)
			progress.advance(task)
			return result

	async def main(): # noqa
		client = NBIAClient()
		semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent tasks

		response_list = []
		# Define queries
		# response1 = client.query(progress, NBIA_ENDPOINTS.GET_COLLECTIONS)
		# response2 = client.query(progress, NBIA_ENDPOINTS.GET_MODALITY_VALUES)
		# response3 = client.query(progress, NBIA_ENDPOINTS.GET_MODALITY_PATIENT_COUNT)
		# response4 = client.query(progress, NBIA_ENDPOINTS.GET_PATIENTS)
		response_list.append(
			client.query(
				NBIA_ENDPOINTS.GET_SERIES,
				params={'Modality': 'RTSTRUCT', 'Collection': 'NSCLC-Radiomics'},
			)
		)
		responses = await asyncio.gather(*response_list)
		with RichProgressBar(
			'[progress.description]{task.description}',
			BarColumn(),
			'[progress.percentage]{task.percentage:>3.0f}%',
			SpinnerColumn(),
			'Time elapsed:',
			TimeElapsedColumn(),
			transient=True,
		) as progress:

			# Execute queries concurrently
			logger.info(f'Found {len(responses)} responses')
			totalcount = 0
			for resp in responses:
				logger.info(f'Found {len(resp)} items')
				totalcount += len(resp)

			task = progress.add_task('Fetching SOPInstanceUIDs...', total=totalcount)

			rt_df = pd.DataFrame(responses[0])
			console.print(rt_df)

			# only subset to first 50
			rt_df = rt_df.head(50)

			sop_tasks = {
				s.SeriesInstanceUID: get_instance_uids_with_semaphore(
					client, s.SeriesInstanceUID, progress, semaphore, task
				)
				for s in rt_df.itertuples()
			}

			sop_responses = await asyncio.gather(*sop_tasks.values())

			series_to_sop = {
				uid: response[0] 
				for uid, response in zip(sop_tasks.keys(), sop_responses)
			}

			new_params = []
			for key, value in series_to_sop.items():
				new_params.append({'SeriesInstanceUID': key, 'SOPInstanceUID': value['SOPInstanceUID']})

			sop_df = pd.DataFrame(new_params)

			console.print(sop_df)
			sop_df.to_csv('SOPs.csv', index=False)

			progress.remove_task(task)

			new_task = progress.add_task('Downloading images...', total=len(series_to_sop))


			download_tasks = {
				uid: get_image_with_semaphore(
					client, uid, sop['SOPInstanceUID'], progress, semaphore, new_task
				)
				for uid, sop in series_to_sop.items()
			}

			download_responses = await asyncio.gather(*download_tasks.values())

			download_df = pd.DataFrame(download_responses)
			console.print(download_df)



	asyncio.run(main())
