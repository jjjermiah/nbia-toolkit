from pydicom.datadict import dictionary_VR
from pydicom.datadict import tag_for_keyword
from pydicom._dicom_dict import DicomDictionary
import pandas as pd
from typing import Any, Union, List


def convert_element_to_int(element_str: str) -> int:
    """
    Converts a DICOM element string representation to an integer.

    Args:
        element_str (str): The DICOM element string representation.

    Returns:
        int: The converted integer value.

    Examples:
        >>> convert_element_to_int('(0028,0010)')
        2621456

    Raises:
        ValueError: If the element format is invalid.

    """
    if element_str.startswith(">"):
        return -1

    elements: list[str] = element_str.strip("()'").split(",")

    # Check if the element has the correct structure
    if len(elements) != 2:
        raise ValueError(
            f"Invalid element format. Element must have the structure '(<INT>,<INT>)': {element_str}"
        )

    # Convert each element from string to integer
    elements_int: list[int]
    elements_int = [int(elem, base=16) for elem in elements]

    # Combine the integers into a single integer
    combined_int: int = (elements_int[0] << 16) + elements_int[1]

    return combined_int


def convert_int_to_element(combined_int: int) -> str:
    """
    Converts a combined integer into a DICOM element string representation.

    Args:
        combined_int (int): The combined integer to be converted.

    Returns:
        str: The DICOM element string representation of the combined integer.

    Examples:
        >>> convert_int_to_element(0x00080060)
        (0008,0060)
        >>> convert_int_to_element(524384)
        (0008,0060)
    """
    assert isinstance(combined_int, int), "combined_int must be an integer."

    if combined_int == -1:
        return "Unknown"

    # Split the integer into two parts
    # i.e 131073 should become (2,1)
    part1: int = combined_int >> 16  # shift right by 16 bits
    part2: int = combined_int & 0xFFFF  # bitwise AND with 0xFFFF (16 bits)

    # Convert the integers to hex strings
    part1_str: str = hex(part1)[2:]
    part2_str: str = hex(part2)[2:]

    # (2,1) should become (0002,0001)
    part1_str = part1_str.zfill(4)
    part2_str = part2_str.zfill(4)

    # capitalize any lowercase letters
    part1_str = part1_str.upper()
    part2_str = part2_str.upper()

    # Combine the hex strings into a single string
    combined_str: str = f"({part1_str},{part2_str})"

    return combined_str


def LOOKUP_TAG(keyword: str) -> int:
    """
    Looks up a DICOM tag based on the keyword. A wrapper around the pydicom's `tag_for_keyword` function.
    """
    tag: int | None = tag_for_keyword(keyword=keyword)
    if tag is None:
        raise (ValueError(f"Tag not found for keyword: {keyword}"))
    return tag


def element_VR_lookup(element_str: str) -> tuple[int, str]:
    """
    Looks up the VR (Value Representation) for a given DICOM element.

    Args:
        element_str (str): The DICOM element as a string.

    Returns:
        tuple[int, str]: A tuple containing the combined integer representation of the element and its VR.
    """

    combined_int: int = convert_element_to_int(element_str=element_str)
    if combined_int == -1:
        return (-1, "Unknown")

    VR: str
    try:
        VR = dictionary_VR(tag=combined_int)
    except KeyError:
        VR = "Unknown,KeyError"

    return (combined_int, VR)


def getSeriesModality(series_tags_df: pd.DataFrame) -> str:
    """
    Retrieves the modality of a DICOM series.

    Args:
        series_tags_df (pd.DataFrame): A DataFrame containing DICOM series tags.

    Returns:
        str: The modality of the DICOM series.

    Raises:
        ValueError: If the modality tag is not found in the DICOM dictionary.
    """
    modality_tag: int | None
    modality_tag = LOOKUP_TAG(keyword="Modality")

    if modality_tag is None:
        raise ValueError("Modality tag not found in the DICOM dictionary.")

    modality_tag_element: str = convert_int_to_element(combined_int=modality_tag)

    modality_row: pd.DataFrame = series_tags_df[
        series_tags_df["element"] == modality_tag_element
    ]
    modality: str = modality_row["data"].values[0]

    return modality


def subsetSeriesTags(series_tags_df: pd.DataFrame, element: str) -> pd.DataFrame:
    """
    Subsets a DataFrame containing DICOM series tags based on the start and end elements.
    """

    locs: pd.DataFrame
    locs = series_tags_df[series_tags_df["element"].str.contains(element)]

    if len(locs) == 0:
        raise ValueError("Element not found in the series tags.")

    if len(locs) > 2:
        raise ValueError("More than two elements found in the series tags.")

    return series_tags_df.iloc[locs.index[0] : locs.index[1]]


def getReferencedFrameOfReferenceSequence(series_tags_df: pd.DataFrame) -> pd.DataFrame:
    modality = getSeriesModality(series_tags_df=series_tags_df)
    if modality != "RTSTRUCT":
        raise ValueError("Series is not an RTSTRUCT.")

    tag: int = LOOKUP_TAG(keyword="ReferencedFrameOfReferenceSequence")

    ReferencedFrameOfReferenceSequence_element: str = convert_int_to_element(
        combined_int=tag
    )

    df: pd.DataFrame = subsetSeriesTags(
        series_tags_df=series_tags_df,
        element=ReferencedFrameOfReferenceSequence_element,
    )

    return df


def getReferencedSeriesUIDS(series_tags_df: pd.DataFrame) -> List[str]:
    """
    Given a DataFrame containing DICOM series tags, retrieves the SeriesInstanceUIDs of the referenced series.
    Useful for RTSTRUCT DICOM files to find the series that the RTSTRUCT references.
    TODO:: implement SEG and RTDOSE

    Args:
        series_tags_df (pd.DataFrame): A DataFrame containing DICOM series tags.

    Returns:
        List[str]: A list of SeriesInstanceUIDs of the referenced series.

    Raises:
        ValueError: If the series is not an RTSTRUCT.
    """

    # "SeriesInstanceUID" ---LOOKUP_TAG--> 2097166 ---convert_int_to_element--> (0020,000E)
    SeriesInstanceUIDtag: int = LOOKUP_TAG(keyword="SeriesInstanceUID")
    SeriesInstanceUID_element: str = convert_int_to_element(
        combined_int=SeriesInstanceUIDtag
    )

    search_space: pd.DataFrame = getReferencedFrameOfReferenceSequence(
        series_tags_df=series_tags_df
    )

    value: pd.DataFrame = search_space[
        search_space["element"].str.contains(SeriesInstanceUID_element)
    ]

    UIDS: list[str] = value["data"].to_list()

    return UIDS
