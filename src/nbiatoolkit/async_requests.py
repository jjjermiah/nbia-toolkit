import asyncio
import json
from typing import Any, Dict, List

import aiohttp
from tenacity import (
	retry,
	retry_if_exception_type,
	stop_after_attempt,
	wait_exponential,
)

from nbiatoolkit.logging_config import logger
from nbiatoolkit.utils import NBIA_BASE_URLS


# Retry settings using tenacity
@retry(
	stop=stop_after_attempt(10),
	wait=wait_exponential(multiplier=1, min=1, max=25),
	retry=retry_if_exception_type(aiohttp.ClientError),
)
async def async_get_request(url: str, headers: dict, params: dict, timeout: int = 60):
	try:
		# Setting up a timeout for the request
		async with aiohttp.ClientSession(
			raise_for_status=True
		) as session:
			async with session.get(url, headers=headers, params=params) as response:
				if 200 <= response.status < 300:  # Accepting any 2xx response
					logger.info(f'Successful request with status code {response.status}')
					return await response.read()
				else:
					logger.error(
						f'Failed with status code {response.status}. Headers: {response.headers}'
					)
					return None
	except aiohttp.ClientResponseError as e:
		logger.error(f'Request failed: {e.status}. Error: {e.message}')
		raise
	except aiohttp.ClientError as e:
		logger.error(f'Client error: {str(e)}')
		raise
	except asyncio.TimeoutError as e:
		logger.error('Request timed out')
		raise


class NoContentError(Exception):
	pass


class UnexpectedResponseStructureError(Exception):
	pass


class JSONDecodingError(Exception):
	pass


class JSONDataAccessError(Exception):
	pass


async def async_query_api(
	endpoint: str,
	params: Dict[str, str],
	headers: Dict[str, str],
	max_retries: int = 10,
	base_url: str = NBIA_BASE_URLS['NBIA'].value,
) -> List[Any]:
	query_url = base_url + endpoint
	logger.info(f'Querying {query_url} with params: {params}')
	content = await async_get_request(
		url=query_url, headers=headers, params=params, timeout=max_retries
	)

	if not content:
		logger.warning(f'No content returned for query: {query_url}')
		msg = 'No content returned'
		raise NoContentError(msg)

	content_str = content.decode('utf-8')

	try:
		json_response = json.loads(content_str)
		if json_response and isinstance(json_response, list) and len(json_response) > 0:
			return json_response
		else:
			logger.error(f'Unexpected response structure: {json_response}')
	except json.JSONDecodeError as e:
		logger.error(f'JSON decoding failed: {e}')
		msg = f'JSON decoding failed: {e}'
		raise JSONDecodingError(msg) from e
	except (KeyError, IndexError) as e:
		logger.error(f'Error accessing JSON data: {e}')
		msg = f'Error accessing JSON data: {e}'
		raise JSONDataAccessError(msg) from e
	except Exception as e:
		logger.error(f'Unexpected response structure: {e}')
		msg = 'Unexpected response structure'
		raise UnexpectedResponseStructureError(msg) from e
	return []
