from src.nbiatoolkit.dicomsort.helper_functions import (
    parseDICOMKeysFromFormat,
    sanitizeFileName,
    _truncateUID,
)
import pytest

###############################################################################
# parseDICOMKeysFromFormat


def test_parseDICOMKeysFromFormat():
    targetPattern = "%PatientID-%StudyDate"
    expected_format = "%(PatientID)s-%(StudyDate)s"
    expected_keys = ["PatientID", "StudyDate"]

    format_string, keys = parseDICOMKeysFromFormat(targetPattern)

    assert format_string == expected_format
    assert keys == expected_keys


def test_parseDICOMKeysFromFormat_no_keys():
    targetPattern = "some string without keys"
    expected_format = "some string without keys"
    expected_keys = []

    format_string, keys = parseDICOMKeysFromFormat(targetPattern)

    assert format_string == expected_format
    assert keys == expected_keys


def test_parseDICOMKeysFromFormat_multiple_keys():
    targetPattern = "%PatientID-%StudyDate-%SeriesNumber"
    expected_format = "%(PatientID)s-%(StudyDate)s-%(SeriesNumber)s"
    expected_keys = ["PatientID", "StudyDate", "SeriesNumber"]

    format_string, keys = parseDICOMKeysFromFormat(targetPattern)

    assert format_string == expected_format
    assert keys == expected_keys


def test_parseDICOMKeysFromFormat_duplicate_keys():
    targetPattern = "%PatientID-%StudyDate-%PatientID"
    expected_format = "%(PatientID)s-%(StudyDate)s-%(PatientID)s"
    expected_keys = ["PatientID", "StudyDate", "PatientID"]

    format_string, keys = parseDICOMKeysFromFormat(targetPattern)

    assert format_string == expected_format
    assert keys == expected_keys


###############################################################################
# sanitizeFileName


def test_sanitizeFileName_no_special_characters():
    fileName = "test_file_name"
    sanitized_name = sanitizeFileName(fileName)
    assert sanitized_name == fileName


def test_sanitizeFileName_with_special_characters():
    fileName = "file<name>:with?special*characters"
    sanitized_name = sanitizeFileName(fileName)
    assert sanitized_name == "file_name_with_special_characters"


def test_sanitizeFileName_with_spaces():
    fileName = "file name with spaces"
    sanitized_name = sanitizeFileName(fileName)
    assert sanitized_name == "file_name_with_spaces"


def test_sanitizeFileName_empty_string():
    fileName = ""
    sanitized_name = sanitizeFileName(fileName)
    assert sanitized_name == ""


def test_sanitizeFileName_assertions():
    with pytest.raises(AssertionError):
        sanitizeFileName(None)  # type: ignore
    with pytest.raises(AssertionError):
        sanitizeFileName(123)  # type: ignore


###############################################################################
# _truncateUID


@pytest.fixture(scope="session")
def uid():
    uid = "1.3.6.1.4.1.14519.5.2.1.215314536760363548451614931725770729635"
    return uid


def test__truncateUID_with_valid_inputs(uid):
    lastDigits = 5
    expected_output = "29635"
    assert _truncateUID(uid, lastDigits) == expected_output


def test__truncateUID_with_lastDigits_greater_than_length_of_UID(uid):
    lastDigits = 100
    expected_output = uid
    assert _truncateUID(uid, lastDigits) == expected_output


def test__truncateUID_with_invalid_input_types(uid):
    lastDigits = "5"
    with pytest.raises(AssertionError):
        _truncateUID(uid, lastDigits)  # type: ignore


def test__truncateUID_with_None_input(uid):
    lastDigits = None
    with pytest.raises(AssertionError):
        _truncateUID(uid, lastDigits)  # type: ignore
