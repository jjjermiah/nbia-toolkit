from requests.exceptions import JSONDecodeError as JSONDecodeError
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import Union, Any, Dict, List, Literal, Optional, Tuple
import pandas as pd
import requests
from enum import Enum


# so that users can decide between a List or a pd.DataFrame
class ReturnType(Enum):
    LIST = "list"
    DATAFRAME = "dataframe"

    # change .value so that DATAFRAME returns "pd.DataFrame"


def clean_html(html_string: str) -> str:
    """
    Cleans the given HTML string by removing HTML tags and replacing special characters.

    Args:
        html_string (str): The input HTML string to be cleaned.

    Returns:
        str: The cleaned text content without HTML tags and special characters.
    """
    assert isinstance(html_string, str), "The input must be a string"
    assert html_string != "", "The input string cannot be empty"
    soup = BeautifulSoup(html_string, "html.parser")
    text_content = soup.get_text(separator=" ", strip=True)
    text_content = text_content.replace("\xa0", " ")
    return text_content


def convertMillis(millis: int) -> str:
    """
    Convert milliseconds to a formatted date string.

    Args:
        millis (int): The number of milliseconds to convert.

    Returns:
        str: The formatted date string in the format 'YYYY-MM-DD'.

    Raises:
        AssertionError: If the input is not an integer.
    """
    assert isinstance(millis, int), "The input must be an integer"
    return datetime.fromtimestamp(millis / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")


def convertDateFormat(
    input_date: Union[str, datetime], format: str = "%Y/%m/%d"
) -> str:
    """
    Converts the input date to the desired format.

    Args:
        input_date (str): The date to be converted.

    Returns:
        str: The converted date in the format "YYYY/MM/DD".

    Raises:
        ValueError: If the input date has an invalid format.
    """
    # List of possible date formats with only days, months, and years
    possible_formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y%m%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
    ]
    if isinstance(input_date, datetime):
        return input_date.strftime(format)

    # Try parsing the input date with each possible format
    for date_format in possible_formats:
        try:
            parsed_date = datetime.strptime(input_date, date_format)
            # If parsing is successful, format the date in YYYY/MM/DD and return
            return parsed_date.strftime(format)
        except ValueError:
            pass  # If parsing fails, continue with the next format
    # If none of the formats match, raise an exception or return a default value
    raise ValueError("Invalid date format: {}".format(input_date))


def parse_response(response: requests.Response) -> List[dict[Any, Any]]:
    """
    Response will be either JSON or bytes

    """
    content_type: str = response.headers.get("content-type", "")

    assert (
        response.status_code == 200
    ), "The response status code must be 200 OK but is {}".format(response.status_code)
    # TODO:: describe error 204

    if not "application/json" in content_type:
        if response.content == b"":
            raise ValueError(
                "The response content is empty. "
                "Check your request parameters and try again."
            )
        else:
            raise ValueError(
                "The response content type must be 'application/json' but is {}".format(
                    content_type
                )
            )

    try:
        response_list = response.json()
    except JSONDecodeError:
        raise JSONDecodeError("Failed to decode JSON response")
    else:
        if not isinstance(response_list, list):
            raise TypeError(
                "The JSON response must be a dictionary but is a {}".format(
                    type(response_list)
                )
            )

    return response_list
