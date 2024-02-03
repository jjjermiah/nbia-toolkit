from bs4 import BeautifulSoup
from datetime import datetime


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
    soup = BeautifulSoup(html_string, 'html.parser')
    text_content = soup.get_text(separator=' ', strip=True)
    text_content = text_content.replace('\xa0', ' ')
    return text_content


from datetime import datetime

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
    return datetime.fromtimestamp(millis / 1000.0).strftime('%Y-%m-%d')