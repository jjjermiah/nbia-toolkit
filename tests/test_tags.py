import pytest
from src.nbiatoolkit import NBIAClient
from src.nbiatoolkit.dicomtags.tags import convert_int_to_element
from src.nbiatoolkit.dicomtags.tags import convert_element_to_int
from src.nbiatoolkit.dicomtags.tags import LOOKUP_TAG
from src.nbiatoolkit.dicomtags.tags import *


def test_convert_int_to_element():
    # Test case 1: combined_int = 0x00080060
    result = convert_int_to_element(0x00080060)
    assert result == "(0008,0060)", f"Expected (0008,0060), but got {result}"

    # Test case 2: combined_int = 524384
    result = convert_int_to_element(524384)
    assert result == "(0008,0060)", f"Expected (0008,0060), but got {result}"

    # Test case 3: combined_int = -1
    result = convert_int_to_element(-1)
    assert result == "Unknown", f"Expected Unknown, but got {result}"

    # Test case 4: combined_int = 0
    result = convert_int_to_element(0)
    assert result == "(0000,0000)", f"Expected (0000,0000), but got {result}"

    # Test case 5: combined_int = 65535
    result = convert_int_to_element(65535)
    assert result == "(0000,FFFF)", f"Expected (0000,FFFF), but got {result}"

    print("All test cases passed!")


def test_convert_element_to_int():
    # Test case 1: element_str = '(0028,0010)'
    result = convert_element_to_int("(0028,0010)")
    assert result == 2621456, f"Expected 2621456, but got {result}"

    # Test case 2: element_str = '(0008,0060)'
    result = convert_element_to_int("(0008,0060)")
    assert result == 524384, f"Expected 524384, but got {result}"

    # Test case 3: element_str = '(0000,0000)'
    result = convert_element_to_int("(0000,0000)")
    assert result == 0, f"Expected 0, but got {result}"

    # Test case 4: element_str = '(0000,FFFF)'
    result = convert_element_to_int("(0000,FFFF)")
    assert result == 65535, f"Expected 65535, but got {result}"

    # Test case 5: element_str = '>Unknown'
    result = convert_element_to_int(">Unknown")
    assert result == -1, f"Expected -1, but got {result}"

    print("All test cases passed!")


def test_LOOKUP_TAG():
    # Test case 1: keyword = "PatientName"
    result = LOOKUP_TAG("PatientName")
    assert result == 0x00100010, f"Expected 0x00100010, but got {result}"

    # Test case 2: keyword = "StudyDate"
    result = LOOKUP_TAG("StudyDate")
    assert result == 0x00080020, f"Expected 0x00080020, but got {result}"

    # Test case 3: keyword = "UnknownKeyword"
    try:
        LOOKUP_TAG("UnknownKeyword")
    except ValueError as e:
        assert (
            str(e) == "Tag not found for keyword: UnknownKeyword"
        ), f"Expected 'Tag not found for keyword: UnknownKeyword', but got {str(e)}"
    else:
        assert False, "Expected ValueError to be raised for unknown keyword"

    print("All test cases passed!")


def test_element_VR_lookup():
    # Test case 1: element_str = '(0028,0010)'
    result = element_VR_lookup("(0028,0010)")
    assert result == (2621456, "US"), f"Expected (2621456, 'US'), but got {result}"

    # Test case 2: element_str = '(0008,0060)'
    result = element_VR_lookup("(0008,0060)")
    assert result == (524384, "CS"), f"Expected (524384, 'CS'), but got {result}"

    # Test case 3: element_str = '(0000,0000)'
    result = element_VR_lookup("(0000,0000)")
    assert result == (0, "UL"), f"Expected (0, 'UL'), but got {result}"

    # Test case 4: element_str = '(0000,FFFF)'
    result = element_VR_lookup("(0000,FFFF)")
    assert result == (
        65535,
        "Unknown,KeyError",
    ), f"Expected (65535, 'Unknown,KeyError'), but got {result}"

    # Test case 5: element_str = '>Unknown'
    result = element_VR_lookup(">Unknown")
    assert result == (-1, "Unknown"), f"Expected (-1, 'Unknown'), but got {result}"

    print("All test cases passed!")


@pytest.fixture(scope="session")
def client():
    return NBIAClient(return_type="dataframe")


@pytest.fixture(scope="session")
def series(client):
    return client.getSeries(Collection="Pediatric-CT-SEG", Modality="RTSTRUCT")


@pytest.fixture(scope="session")
def RTSTRUCT_Series(series):
    return series[series["Modality"] == "RTSTRUCT"]


@pytest.fixture(scope="session")
def RTSTRUCT_Tags(client, RTSTRUCT_Series):
    seriesUID = RTSTRUCT_Series["SeriesInstanceUID"].values[0]
    assert seriesUID is not None, "Expected seriesUID to be returned, but got None"

    tags_df = client.getDICOMTags(seriesUID)
    assert tags_df is not None, "Expected tags to be returned, but got None"

    return tags_df


def test_getDICOMTags(RTSTRUCT_Tags):
    seriesUIDS = getReferencedSeriesUIDS(RTSTRUCT_Tags)
    expected = ["1.3.6.1.4.1.14519.5.2.1.133742245714270925254982946723351496764"]
    assert seriesUIDS == expected, f"Expected {expected}, but got {seriesUIDS}"


def test_getSeriesModality(RTSTRUCT_Tags):
    modality = getSeriesModality(RTSTRUCT_Tags)
    assert modality == "RTSTRUCT", f"Expected 'RTSTRUCT', but got {modality}"

    # Test case 2: modality tag not found
    RTSTRUCT_Tags.drop(
        RTSTRUCT_Tags[RTSTRUCT_Tags["element"] == "(0008,0060)"].index, inplace=True
    )

    with pytest.raises(IndexError) as e:
        getSeriesModality(RTSTRUCT_Tags)
