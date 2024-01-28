import re
from typing import Tuple, List


def parseDICOMKeysFromFormat(targetPattern: str) -> Tuple[str, List[str]]:
    """
    Parse the target pattern to create a format string with named placeholders
    and extract a list of DICOM keys.

    The target pattern is a string with placeholders matching '%<DICOMKey>'.
    This method converts placeholders into a format string with named placeholders
    and creates a list of DICOM keys contained within the placeholders.

    Returns:
        Tuple[str, List[str]]: A tuple containing the format string and a list of DICOM keys.

    Example usage:
        fmt, keys = parseDICOMKeysFromFormat(targetPattern)
        print(fmt)  # "%(PatientID)s-%(StudyDate)s"
        print(keys)  # ['PatientID', 'StudyDate']
    """

    # Compile the regex pattern for efficiency
    dicom_key_pattern = re.compile(r"%([A-Za-z]+)")
    keys = dicom_key_pattern.findall(targetPattern)
    # Use the same compiled pattern for replacing
    formatted_pattern = dicom_key_pattern.sub(r"%(\1)s", targetPattern)

    return formatted_pattern, keys


def sanitizeFileName(fileName: str) -> str:
    """
    Sanitize the file name by replacing potentially dangerous characters.
    """
    assert fileName is not None
    assert isinstance(fileName, str)
    # Define a pattern for disallowed filename characters and their replacements
    disallowed_characters_pattern = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
    # Replace disallowed characters with an underscore
    sanitized_name = disallowed_characters_pattern.sub("_", fileName)

    # replace spaces with underscores
    sanitized_name = sanitized_name.replace(" ", "_")

    # Remove subsequent underscores
    sanitized_name = re.sub(r"(_{2,})", "_", sanitized_name)

    return sanitized_name


def truncateUID(uid: str, lastDigits: int = 5) -> str:
    """
    Truncate the UID to the last n characters (includes periods & underscores).
    If the UID is shorter than n characters, the entire UID is returned.
    """
    assert uid is not None
    assert isinstance(uid, str)
    assert isinstance(lastDigits, int)
    # Truncate the UID to the last n digits
    truncated_uid = uid[-lastDigits:]
    return truncated_uid
