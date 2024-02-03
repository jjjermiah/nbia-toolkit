from src.nbiatoolkit.utils.parsers import clean_html, convertMillis
from datetime import datetime
import pytest
def test_clean_html_valid_input():
    # Test case for valid input with HTML tags and special characters
    html_string = "<p>This is <b>bold</b> text with special characters: &amp; &lt; &gt;</p>"
    expected_output = "This is bold text with special characters: & < >"
    assert clean_html(html_string) == expected_output

def test_clean_html_empty_input():
    # Test case for empty input string
    html_string = ""
    expected_output = ""
    with pytest.raises(AssertionError) as e:
        clean_html(html_string)

def test_clean_html_no_html_tags():
    # Test case for input string without any HTML tags
    html_string = "This is a plain text without any HTML tags"
    expected_output = "This is a plain text without any HTML tags"
    assert clean_html(html_string) == expected_output

def test_clean_html_special_characters_only():
    # Test case for input string with only special characters
    html_string = "&amp; &lt; &gt;"
    expected_output = "& < >"
    assert clean_html(html_string) == expected_output


def test_convertMillis_valid_input():
    # Test case for valid input
    target_date = datetime(2021, 9, 1)
    millis = int(target_date.timestamp() * 1000)
    expected_output = "2021-09-01"
    assert convertMillis(millis) == expected_output

def test_convertMillis_invalid_input():
    # Test case for invalid input
    millis = "1630444800000"  # Invalid input: string instead of integer
    try:
        convertMillis(millis)  # type: ignore
        assert False, "Expected AssertionError"
    except AssertionError as e:
        assert str(e) == "The input must be an integer"