from __future__ import annotations

import asyncio
import json

import aiohttp
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from nbiatoolkit.logging_config import logger

MAX_CACHE_SIZE = 512

# Retry settings constants
MAX_ATTEMPTS = 10
MULTIPLIER = 1
MIN_WAIT = 1
MAX_WAIT = 25


class UnexpectedResponseStructureError(Exception):
    pass


class RetryHandlerMixin:
    """Mixin class to handle retry logic for HTTP requests."""

    async def __aenter__(self) -> RetryHandlerMixin:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass

    @retry(
        # Stop after 10 failed attempts
        stop=stop_after_attempt(
            MAX_ATTEMPTS
        ),  # Stop after MAX_ATTEMPTS failed attempts
        wait=wait_exponential(
            multiplier=MULTIPLIER, min=MIN_WAIT, max=MAX_WAIT
        ),  # Wait time increases exponentially between retries
        retry=retry_if_exception_type(
            aiohttp.ClientError
        ),  # Retry only if an aiohttp.ClientError is raised
    )
    async def async_get_request(
        self, url: str, headers: dict, params: dict
    ) -> bytes | None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers=headers, params=dict(params)
                ) as response:
                    if 200 <= response.status < 300:
                        return await response.read()
                    else:
                        msg = (
                            f"Failed with status code {response.status}. "
                            f"Headers: {response.headers}"
                        )
                        logger.error(msg)
                        return None
        except aiohttp.ClientResponseError as e:
            logger.error(f"Request failed: {e.status}. Error: {e.message}")
            raise e
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {str(e)}")
            raise e
        except asyncio.TimeoutError as e:
            logger.error("Request timed out")
            raise e

    async def parse_json_response(
        self, response: bytes, encoding: str = "utf-8"
    ) -> list[dict]:
        content_str = response.decode(encoding)
        try:
            json_response = json.loads(content_str)
        except Exception as e:
            logger.error(f"Error decoding JSON response: {e}")
            return []

        match json_response:
            case list():
                return json_response
            case _:
                msg = "Unexpected response structure. Expected a list."
                msg += f"Received: {type(json_response)}"
                logger.error(msg)
                raise UnexpectedResponseStructureError(msg)
