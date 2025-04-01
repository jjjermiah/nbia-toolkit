from __future__ import annotations

import io
import json
from abc import ABC, abstractmethod
from asyncio import Semaphore, TimeoutError
from functools import wraps
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientSession
from async_lru import alru_cache
from frozendict import frozendict
from tenacity import (
	retry,
	retry_if_exception_type,
	stop_after_attempt,
	wait_exponential,
)

from nbiatoolkit.logging_config import logger


# Automatically apply nest_asyncio to make the package work seamlessly in Jupyter
try:
	import nest_asyncio

	nest_asyncio.apply()
	logger.debug(
		'nest_asyncio automatically applied for Jupyter notebook compatibility'
	)
except Exception as e:
	logger.debug(
		f'Note: nest_asyncio not applied: {str(e)}. This is normal in non-Jupyter environments.'
	)

# Default values for API client configuration
MAX_CONCURRENT_REQUESTS = 15
MAX_ATTEMPTS = 10
WAIT_MULTIPLIER = 1.0
MIN_WAIT = 1
MAX_WAIT = 25
TIMEOUT = 30.0


class UnexpectedResponseStructureError(Exception):
	pass


class InvalidBinaryDataError(Exception):
	pass


def freezeargs(func):
	"""Convert a mutable dictionary into immutable.
	Useful to be compatible with cache
	"""

	@wraps(func)
	def wrapped(*args, **kwargs):
		args = (frozendict(arg) if isinstance(arg, dict) else arg for arg in args)
		kwargs = {
			k: frozendict(v) if isinstance(v, dict) else v for k, v in kwargs.items()
		}
		return func(*args, **kwargs)

	return wrapped


class FailedQueryError(Exception):
	"""Exception raised for failed API query attempts.

	Parameters
	----------
	endpoint : str
	    The API endpoint that was queried
	base_url : str
	    The base URL used for the API request
	params : dict
	    The parameters used in the API request

	Examples
	--------
	>>> raise FailedQueryError('/patients', 'https://api.example.com', {'id': '123'})
	"""

	def __init__(self, endpoint: str, base_url: str, params: dict) -> None:
		message = (
			f'Query failed for endpoint: {endpoint} at {base_url} with params: {params}'
		)
		super().__init__(message)


class BaseClient(ABC):
	"""Abstract base class for API clients.

	Parameters
	----------
	base_url : str
	    Base URL for the API
	    Logging level, by default "INFO"
	"""

	def __init__(
		self,
		base_url: str,
		max_concurrent_requests: int | None = None,
		max_attempts: int | None = None,
		wait_multiplier: float | None = None,
		min_wait: int | None = None,
		max_wait: int | None = None,
		timeout_seconds: float | None = None,
	) -> None:
		self.base_url: str = base_url
		self.max_concurrent_requests = (
			max_concurrent_requests or MAX_CONCURRENT_REQUESTS
		)
		self.max_attempts = max_attempts or MAX_ATTEMPTS
		self.wait_multiplier = wait_multiplier or WAIT_MULTIPLIER
		self.min_wait = min_wait or MIN_WAIT
		self.max_wait = max_wait or MAX_WAIT
		self.timeout_seconds = timeout_seconds or TIMEOUT
		self._semaphore: Semaphore = Semaphore(self.max_concurrent_requests)

	@property
	@abstractmethod
	def headers(self) -> dict[str, str]:
		"""Headers must be defined by concrete subclasses.

		Returns
		-------
		dict[str, str]
		    HTTP headers to be used in requests
		"""
		pass

	async def _request(
		self,
		endpoint: str,
		params: dict[str, str] | None = None,
	) -> bytes:
		url = self.base_url + endpoint
		logger.debug(
			'Making request to %s with %s', url, dict(params) if params else {}
		)

		result = await self.async_get_request(
			url=url,
			headers=self.headers,
			params=params or {},
		)

		if not result:
			msg = f'Request to {url} failed or returned empty.'
			logger.error(msg)
			raise FailedQueryError(endpoint, self.base_url, params or {})
		return result

	@freezeargs
	@alru_cache(maxsize=128)
	async def query_json(
		self, endpoint: str, params: dict[str, str] | None = None
	) -> list[dict]:
		"""Query API endpoint and return parsed JSON response.

		Parameters
		----------
		endpoint : str
		    API endpoint to query
		params : dict[str, str] | None, optional
		    Query parameters, by default None

		Returns
		-------
		list[dict]
		    Parsed JSON response

		Raises
		------
		FailedQueryError
		    If the request fails or returns empty
		"""

		raw_bytes = await self._request(endpoint, params)
		return await self.parse_json_response(raw_bytes)

	async def query_bytes(
		self, endpoint: str, params: dict[str, str] | None = None
	) -> bytes:
		"""Query API endpoint and return raw bytes response.

		Parameters
		----------
		endpoint : str
		    API endpoint to query
		params : dict[str, str] | None, optional
		    Query parameters, by default None

		Returns
		-------
		bytes
		    Raw bytes response

		Raises
		------
		FailedQueryError
		    If the request fails or returns empty
		"""
		return await self._request(endpoint, params)

	async def async_get_request(
		self, url: str, headers: Dict[str, Any], params: Dict[str, Any]
	) -> Optional[bytes]:
		"""Make an async GET request with retry logic.

		Parameters
		----------
		url : str
		    The URL to make the GET request to
		headers : Dict[str, Any]
		    Headers to include in the request
		params : Dict[str, Any]
		    Query parameters to include in the request

		Returns
		-------
		Optional[bytes]
		    The response content as bytes if successful, None otherwise
		"""

		@retry(
			stop=stop_after_attempt(self.max_attempts),
			wait=wait_exponential(
				multiplier=self.wait_multiplier, min=self.min_wait, max=self.max_wait
			),
			retry=retry_if_exception_type(aiohttp.ClientError),
		)
		async def _get_request() -> bytes | None:
			"""Inner function to make the actual GET request with retry logic.

			Returns
			-------
			Optional[bytes]
			    The response content as bytes if successful, None otherwise

			Raises
			------
			aiohttp.ClientResponseError
			    When an error response is received from the server
			aiohttp.ClientError
			    When a client-side error occurs
			asyncio.TimeoutError
			    When the request times out
			"""
			try:
				# First acquire the semaphore before creating the session
				async with self._semaphore:
					logger.debug(
						'Sempahore available: %s/%s',
						self._semaphore._value,
						self.max_concurrent_requests,
					)
					try:
						async with (
							ClientSession() as session,
							session.get(
								url,
								headers=headers,
								params=params,
								timeout=self.timeout_seconds,
							) as response,
						):
							if 200 <= response.status < 300:  # noqa
								return await response.read()
							else:
								msg = (
									f'Failed with status code {response.status}. '
									f'Headers: {response.headers}'
								)
								logger.error(msg)
								return None
					finally:
						logger.debug(
							'Released semaphore %s/%s',
							self._semaphore._value,
							self.max_concurrent_requests,
						)
			except aiohttp.ClientResponseError as e:
				logger.error(f'Request failed: {e.status}. Error: {e.message}')
				raise
			except aiohttp.ClientError as e:
				logger.error(f'Client error: {str(e)}')
				raise
			except TimeoutError:
				logger.error('Request timed out')
				raise

		return await _get_request()

	async def parse_json_response(
		self, response: bytes, encoding: str = 'utf-8'
	) -> List[Dict[str, Any]]:
		"""Parse a bytes response as JSON.

		Parameters
		----------
		response : bytes
		    The response bytes to parse
		encoding : str, optional
		    The encoding to use for decoding the bytes, by default 'utf-8'

		Returns
		-------
		List[Dict[str, Any]]
		    The parsed JSON response as a list of dictionaries

		Raises
		------
		UnexpectedResponseStructureError
		    If the response is not a list
		"""
		content_str = response.decode(encoding)
		try:
			json_response = json.loads(content_str)
		except Exception as e:
			logger.error(f'Error decoding JSON response: {e}')
			return []

		match json_response:
			case list():
				return json_response
			case _:
				msg = 'Unexpected response structure. Expected a list.'
				msg += f'Received: {type(json_response)}'
				logger.error(msg)
				raise UnexpectedResponseStructureError(msg)

	async def parse_bytes(self, response: bytes) -> io.BytesIO:
		"""Parse response as binary data.

		Parameters
		----------
		response : bytes
		    The binary response data

		Returns
		-------
		io.BytesIO
		    BytesIO object containing the binary content

		Raises
		------
		InvalidBinaryDataError
		    If the response doesn't appear to be valid binary data
		"""
		if not response or not isinstance(response, bytes):
			msg = f'Invalid binary response: {type(response) if response else "None"}'
			logger.error(msg)
			raise InvalidBinaryDataError(msg)

		# Check for common binary file signatures
		# ZIP file signature: PK\x03\x04
		if response.startswith(b'PK\x03\x04'):
			logger.debug('Detected ZIP file content')
			return io.BytesIO(response)
		# DICOM signature typically at 128 bytes in
		elif len(response) > 132 and response[128:132] == b'DICM':  # noqa: PLR2004
			logger.debug('Detected DICOM file content')
			return io.BytesIO(response)
		# Generic binary check - look for non-printable bytes in first few bytes
		elif any(byte < 9 or (14 < byte < 32) for byte in response[:32]):  # noqa: PLR2004
			logger.debug('Detected generic binary content')
			return io.BytesIO(response)
		else:
			# If we can't confirm it's binary, check if it might be text
			try:
				# Try to decode as text - if it works without errors, it's likely not binary
				response[:100].decode('utf-8')
				msg = 'Response appears to be text data, not binary content'
				logger.error(msg)
				raise InvalidBinaryDataError(msg)
			except UnicodeDecodeError:
				# Failed to decode as text, so it's likely binary
				logger.debug('Detected binary content (failed UTF-8 decode)')
				return io.BytesIO(response)
