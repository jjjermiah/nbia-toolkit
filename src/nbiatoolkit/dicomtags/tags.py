from math import log
import pydicom
from pydicom.datadict import dictionary_VR, tag_for_keyword
import pandas as pd
from typing import List


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

    Args:
        series_tags_df (pd.DataFrame): A DataFrame containing DICOM series tags.
        element (str): The element to subset the DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the subset of the series tags.

    Raises:
        ValueError: If the element is not found in the series tags.
        ValueError: If more than two elements are found in the series tags.
    """

    locs: pd.DataFrame
    locs = series_tags_df[series_tags_df["element"].str.contains(element)]

    if len(locs) == 0:
        raise ValueError("Element not found in the series tags.")

    if len(locs) == 1:
        raise ValueError(
            "Only one element found in the series tags. Ensure element is a sequence"
        )

    if len(locs) > 2:
        raise ValueError("More than two elements found in the series tags.")

    return series_tags_df.iloc[locs.index[0] : locs.index[1] + 1]


def getReferencedFrameOfReferenceSequence(series_tags_df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame containing DICOM series tags, retrieves the ReferencedFrameOfReferenceSequence.

    Args:
        series_tags_df (pd.DataFrame): A DataFrame containing DICOM series tags.

    Returns:
        pd.DataFrame: A DataFrame containing the ReferencedFrameOfReferenceSequence.

    Raises:
        ValueError: If the series is not an RTSTRUCT.

    """
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


def getSequenceElement(
    sequence_tags_df: pd.DataFrame, element_keyword: str
) -> pd.DataFrame:
    """
    Given a DataFrame containing DICOM sequence tags, retrieves the search space
    based on the element keyword.

    Args:
        sequence_tags_df (pd.DataFrame): A DataFrame containing DICOM sequence tags.
        element_keyword (str): The keyword of the element to search for.

    Returns:
        pd.DataFrame: A DataFrame containing the search space based on the element keyword.

    Raises:
        ValueError: If the element is not found in the sequence tags.
        ValueError: If more than two elements are found in the sequence tags.
    """
    tag: int = LOOKUP_TAG(keyword=element_keyword)
    element: str = convert_int_to_element(combined_int=tag)

    df: pd.DataFrame = subsetSeriesTags(
        series_tags_df=sequence_tags_df, element=element
    )

    return df


def camel_case_tag(string: str) -> str:
    """
    Convert a string to camel case.

    Args:
        string (str): The input string to be converted.

    Returns:
        str:  The camel case string.

    Example:
        >>> camel_case_tag("hello world")
        'HelloWorld'

    Note:
        This function does not actually convert to camel case to not modify
        the tags from the DICOM dictionary.
    """
    return "".join(word for word in string.split())


def extract_ROI_info(StructureSetROISequence) -> dict[str, dict[str, str]]:
    """
    Extracts ROI information from the StructureSetROISequence.

    Args:
        StructureSetROISequence (pandas.DataFrame): A pandas DataFrame representing the StructureSetROISequence.

    Returns:
        dict[str, dict[str, str]]: A dictionary containing ROI information, where the key is the ROI number and the value is the ROI information.

    Raises:
        ValueError: If ROI Number is not found in the StructureSetROISequence.
    """

    # Initialize an empty dictionary to store ROI information
    ROISet: dict[str, dict[str, str]] = {}

    # get the rows where name = " ROI Number"
    ROI_indices = StructureSetROISequence[
        StructureSetROISequence["name"] == "ROI Number"
    ].index

    if ROI_indices.empty:
        raise ValueError("ROI Number not found in the StructureSetROISequence.")

    # Iterate between the indices of the ROI numbers, to extract the ROI information
    # add to the dictionary where the key is the ROI number and the value is the ROI information
    for i in range(len(ROI_indices) - 1):
        ROI_number: str = StructureSetROISequence.loc[ROI_indices[i], "data"]

        ROI_info: pd.DataFrame = StructureSetROISequence.loc[
            ROI_indices[i] + 1 : ROI_indices[i + 1] - 1
        ]

        ROISet[ROI_number] = {
            camel_case_tag(string=row["name"]): row["data"]
            for _, row in ROI_info.iterrows()
        }

    return ROISet


def generateFileDatasetFromTags(tags_df: pd.DataFrame) -> pydicom.Dataset:
    """
    Generate a pydicom Dataset object from a DataFrame of DICOM tags.

    Args:
        tags_df (pd.DataFrame): DataFrame containing DICOM tags.

    Returns:
        pydicom.Dataset: A pydicom Dataset object containing the DICOM tags.
    """

    # Create a new FileDataset
    ds = pydicom.Dataset()

    for _, row in tags_df.iterrows():
        tag = convert_element_to_int(row["element"])
        value = row["data"]
        if tag == -1:
            continue
        VR = element_VR_lookup(row["element"])[1]

        ds.add_new(tag=tag, VR=VR, value=value)

    return ds


# def getRTSTRUCT_ROI_info(seriesUID: str) -> dict[str, dict[str, str]]:
#     """
#     Given a SeriesInstanceUID of an RTSTRUCT, retrieves the ROI information.

#     Args:
#         seriesUID (str): The SeriesInstanceUID of the RTSTRUCT.

#     Returns:
#         dict[str, dict[str, str]]: A dictionary containing the ROI information.
#     """

#     RTSTRUCT_Tags = client.getDICOMTags(seriesUID)

#     StructureSetROISequence = getSequenceElement(sequence_tags_df=RTSTRUCT_Tags, element_keyword="StructureSetROISequence")

#     return extract_ROI_info(StructureSetROISequence)
