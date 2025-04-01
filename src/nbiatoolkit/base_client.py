from __future__ import annotations
from abc import ABC, abstractmethod
from aiohttp import ClientSession
from nbiatoolkit.retry_handler import RetryHandlerMixin
from nbiatoolkit.logging_config import logger
from frozendict import frozendict
from functools import wraps

from async_lru import alru_cache


def freezeargs(func):
    """Convert a mutable dictionary into immutable.
    Useful to be compatible with cache
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        args = (frozendict(arg) if isinstance(arg, dict) else arg for arg in args)
        kwargs = {k: frozendict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
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
        message = f"Query failed for endpoint: {endpoint} at {base_url} with params: {params}"
        super().__init__(message)


class BaseClient(RetryHandlerMixin, ABC):
    """Abstract base class for API clients.
    
    Parameters
    ----------
    base_url : str
        Base URL for the API
    log_level : str, optional
        Logging level, by default "INFO"
    """
    
    def __init__(self, base_url: str, log_level: str = "INFO") -> None:
        self.base_url: str = base_url
        self.log_level: str = log_level
        self._session: ClientSession | None = None
    
    async def __aenter__(self) -> BaseClient:
        self._session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self._session:
            await self._session.close()

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

    async def _request(self, endpoint: str, params: dict[str, str] | None = None) -> bytes:
        url = self.base_url + endpoint
        logger.debug("Making request to %s with %s", url, params or {})
        result = await self.async_get_request(url=url, headers=self.headers, params=params or {})
        if not result:
            msg = f"Request to {url} failed or returned empty."
            logger.error(msg)
            raise FailedQueryError(endpoint, self.base_url, params or {})
        return result

    @freezeargs
    @alru_cache(maxsize=128)
    async def query_json(self, endpoint: str, params: dict[str, str] | None = None) -> list[dict]:
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
    
    async def query_bytes(self, endpoint: str, params: dict[str, str] | None = None) -> bytes:
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