from __future__ import annotations

import asyncio
import json
import io

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


class InvalidBinaryDataError(Exception):
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

    async def parse_bytes(self, response: bytes) -> io.BytesIO:
        """Parse response as binary data (e.g., zip file).
        
        Args:
            response: The binary response data
            
        Returns:
            BytesIO object containing the binary content
            
        Raises:
            InvalidBinaryDataError: If the response doesn't appear to be valid binary data
        """
        if not response or not isinstance(response, bytes):
            msg = f"Invalid binary response: {type(response) if response else 'None'}"
            logger.error(msg)
            raise InvalidBinaryDataError(msg)

        # Check for common binary file signatures
        # ZIP file signature: PK\x03\x04
        if response.startswith(b'PK\x03\x04'):
            logger.debug("Detected ZIP file content")
            return io.BytesIO(response)
        # DICOM signature typically at 128 bytes in
        elif len(response) > 132 and response[128:132] == b'DICM':
            logger.debug("Detected DICOM file content")
            return io.BytesIO(response)
        # Generic binary check - look for non-printable bytes in first few bytes
        elif any(byte < 9 or (14 < byte < 32) for byte in response[:32]):
            logger.debug("Detected generic binary content")
            return io.BytesIO(response)
        else:
            # If we can't confirm it's binary, check if it might be text
            try:
                # Try to decode as text - if it works without errors, it's likely not binary
                response[:100].decode('utf-8')
                msg = "Response appears to be text data, not binary content"
                logger.error(msg)
                raise InvalidBinaryDataError(msg)
            except UnicodeDecodeError:
                # Failed to decode as text, so it's likely binary
                logger.debug("Detected binary content (failed UTF-8 decode)")
                return io.BytesIO(response)
