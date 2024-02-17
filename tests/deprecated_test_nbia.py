#####
# pytest -v -n 8

# To run only one of the tests:
# pytest -v -n 8 tests/test_nbia.py::test_getCollections

import pytest
from src.nbiatoolkit import NBIAClient
from tempfile import TemporaryDirectory
import os
import requests


@pytest.fixture(scope="session")
def nbia_client():
    nbia = NBIAClient()
    return nbia


@pytest.fixture(scope="session")
def nbia_collections(nbia_client):
    collections = nbia_client.getCollections()
    return collections


@pytest.fixture(scope="session")
def nbia_patients(nbia_client, nbia_collections):
    patients = nbia_client.getPatients(Collection=nbia_collections[0])
    return patients


@pytest.fixture(scope="session")
def nbia_ModalityValues(nbia_client, nbia_collections):
    modalities = nbia_client.getModalityValues(Collection=nbia_collections[0])
    return modalities


@pytest.fixture(scope="session")
def nbia_patientsByCollectionAndModality(nbia_client, nbia_collections):
    patients = nbia_client.getPatientsByCollectionAndModality(
        Collection=nbia_collections[0], Modality="CT"
    )
    return patients


def test_getModalityValues(nbia_ModalityValues):
    assert isinstance(nbia_ModalityValues, list)
    assert len(nbia_ModalityValues) > 0
    assert isinstance(nbia_ModalityValues[0], str)
    assert len(nbia_ModalityValues[0]) > 0


def test_nbiaclient_access_token(nbia_client):
    assert nbia_client.headers is not None


def test_getCollections(nbia_collections):
    assert isinstance(nbia_collections, list)
    assert len(nbia_collections) > 0


def test_getBodyPartCounts_all(nbia_client):
    bodyparts = nbia_client.getBodyPartCounts()
    assert isinstance(bodyparts, list)
    assert len(bodyparts) > 0
    assert "BodyPartExamined" in bodyparts[0]
    assert "Count" in bodyparts[0]
    assert int(bodyparts[0]["Count"]) > 0


def test_getBodyPartCounts_4DLung(nbia_client):
    bodyparts = nbia_client.getBodyPartCounts(Collection="4D-Lung")
    assert isinstance(bodyparts, list)
    assert len(bodyparts) > 0
    assert isinstance(bodyparts[0], dict)
    assert "BodyPartExamined" in bodyparts[0]
    assert "Count" in bodyparts[0]
    assert bodyparts[0]["BodyPartExamined"] == "LUNG"
    assert int(bodyparts[0]["Count"]) > 0


def test_getCollectionPatientCount(nbia_client):
    patientCount = nbia_client.getCollectionPatientCount()
    assert isinstance(patientCount, list)
    assert len(patientCount) > 0
    assert isinstance(patientCount[0], dict)
    assert "Collection" in patientCount[0]
    assert "PatientCount" in patientCount[0]
    assert int(patientCount[0]["PatientCount"]) > 0


def test_getPatients(nbia_patients):
    assert isinstance(nbia_patients, list)
    assert len(nbia_patients) > 0
    assert isinstance(nbia_patients[0], dict)
    assert "PatientId" in nbia_patients[0]
    assert "PatientName" in nbia_patients[0]
    assert "Collection" in nbia_patients[0]
    assert "PatientSex" in nbia_patients[0]


def test_getNewPatients(nbia_client):
    patients = nbia_client.getNewPatients("CMB-LCA", Date="2022/12/06")
    assert isinstance(patients, list)
    assert len(patients) > 0
    assert isinstance(patients[0], dict)
    assert "PatientId" in patients[0]
    assert "PatientName" in patients[0]
    assert "Collection" in patients[0]
    assert "PatientSex" in patients[0]


def test_failed_getNewPatients(nbia_client):
    with pytest.raises(Exception):
        patients = nbia_client.getNewPatients("TCGA-BLCA", Date="bad_date")
    with pytest.raises(Exception):
        patients = nbia_client.getNewPatients("bad_collection", Date="2019-01-01")


def test_getPatientsByCollectionAndModality(nbia_patientsByCollectionAndModality):
    assert isinstance(nbia_patientsByCollectionAndModality, list)
    assert len(nbia_patientsByCollectionAndModality) > 0
    assert isinstance(nbia_patientsByCollectionAndModality[0], str)
    assert len(nbia_patientsByCollectionAndModality[0]) > 0


def test_getStudies(nbia_client, nbia_collections):
    studies = nbia_client.getStudies(Collection=nbia_collections[0])
    assert studies is not None
    assert isinstance(studies, list)
    assert len(studies) > 0
    assert isinstance(studies[0], dict)


def test_getSeries(nbia_client, nbia_collections, nbia_patients):
    seriesList = nbia_client.getSeries(
        Collection=nbia_collections[0],
        PatientID=nbia_patients[0]["PatientId"],
        Modality="CT",
    )
    assert seriesList is not None
    assert isinstance(seriesList, list)
    assert len(seriesList) > 0
    assert isinstance(seriesList[0], dict)


def test_fail_getSeries(nbia_client, nbia_collections, nbia_patients):
    with pytest.raises(Exception):
        seriesList = nbia_client.getSeries(
            Collection=nbia_collections[0],
            PatientID=nbia_patients[0]["PatientId"],
            Modality="CT",
            SeriesInstanceUID="bad_series_uid",
        )
        assert seriesList is not None
        assert isinstance(seriesList, list)
        assert len(seriesList) > 0
        assert isinstance(seriesList[0], dict)


def test_getNewSeries(nbia_client):
    Date = "01/01/2024"
    series = nbia_client.getNewSeries(Date)
    assert isinstance(series, list) or series is None
    if series is not None:
        assert all(isinstance(s, dict) for s in series)


def test_downloadSeries(nbia_client, nbia_collections, nbia_patients):
    seriesList = nbia_client.getSeries(
        Collection=nbia_collections[0],
        PatientID=nbia_patients[0]["PatientId"],
        Modality="CT",
    )
    filePattern = (
        "%PatientID/%Modality/%SeriesNumber-%SeriesInstanceUID/%InstanceNumber.dcm"
    )
    # create a temporary directory

    tempdir_ = TemporaryDirectory()
    tempdir = tempdir_.name

    nbia_client.downloadSeries(
        SeriesInstanceUID=seriesList[0]["SeriesInstanceUID"],
        downloadDir=tempdir,
        filePattern=filePattern,
    )
    dir = os.listdir(tempdir)

    assert len(dir) == 1
    assert dir[0] == nbia_patients[0]["PatientId"]
    assert os.path.isdir(os.path.join(tempdir, dir[0]))

    modality_dir = os.listdir(os.path.join(tempdir, dir[0]))
    assert len(modality_dir) == 1
    assert modality_dir[0] == "CT"
    assert os.path.isdir(os.path.join(tempdir, dir[0], modality_dir[0]))

    series_dir = os.listdir(os.path.join(tempdir, dir[0], modality_dir[0]))
    assert len(series_dir) == 1
    # only last 5 digits of SeriesInstanceUID are used
    assert series_dir[0] == "{}-{}".format(
        seriesList[0]["SeriesNumber"], seriesList[0]["SeriesInstanceUID"][-5:]
    )
    assert os.path.isdir(os.path.join(tempdir, dir[0], modality_dir[0], series_dir[0]))

    dicom_dir = os.listdir(
        os.path.join(tempdir, dir[0], modality_dir[0], series_dir[0])
    )

    assert len(dicom_dir) == int(seriesList[0]["ImageCount"])
    for file in dicom_dir:
        assert file.endswith(".dcm")
        assert file[:-4].isdigit()


def test_getCollectionDescriptions(nbia_client):
    collectionName = "4D-Lung"
    descriptions = nbia_client.getCollectionDescriptions(collectionName)
    assert isinstance(descriptions, list)
    assert len(descriptions) == 1
    assert isinstance(descriptions[0], dict)
    assert "collectionName" in descriptions[0]
    assert descriptions[0]["collectionName"] == collectionName
    assert "description" in descriptions[0]
    assert "descriptionURI" in descriptions[0]
    assert "lastUpdated" in descriptions[0]


def test_failed_getCollectionDescriptions(nbia_client):
    collectionName = "bad_collection"
    with pytest.raises(ValueError):
        nbia_client.getCollectionDescriptions(collectionName)


def test_getSeriesMetadata_single(nbia_client):
    seriesUID = "1.3.6.1.4.1.14519.5.2.1.6834.5010.227929163446067537882961857921"
    metadata = nbia_client.getSeriesMetadata(seriesUID)
    assert isinstance(metadata, list)
    assert len(metadata) > 0
    assert isinstance(metadata[0], dict)


def test_getSeriesMetadata_multiple(nbia_client):
    seriesUIDs = [
        "1.3.6.1.4.1.14519.5.2.1.6834.5010.227929163446067537882961857921",
        "1.3.6.1.4.1.14519.5.2.1.6834.5010.322628904903035357840500590726",
    ]
    metadata = nbia_client.getSeriesMetadata(seriesUIDs)
    assert isinstance(metadata, list)
    assert len(metadata) > 0
    assert isinstance(metadata[0], dict)
    assert len(metadata) == len(seriesUIDs)


def test_getSeriesMetadata_invalid_input(nbia_client):
    seriesUID = 12345

    with pytest.raises(AssertionError):
        metadata = nbia_client.getSeriesMetadata(seriesUID)

    with pytest.raises(requests.exceptions.RequestException):
        metadata = nbia_client.getSeriesMetadata(str(seriesUID))
        assert metadata is None

    with pytest.raises(requests.exceptions.RequestException):
        seriesUIDs = ["12345", 67890]
        metadata = nbia_client.getSeriesMetadata(seriesUIDs)
        assert metadata is None


def test_nbiaclient_exit(nbia_client):
    with nbia_client:
        collections = nbia_client.getCollections()
        assert not nbia_client._oauth2_client.is_logged_out()
    assert (
        nbia_client._oauth2_client.is_logged_out()
    )  # Assuming there is a method to check if the client is logged out


def test_getDICOMTags(nbia_client: NBIAClient):
    seriesUID = "1.3.6.1.4.1.14519.5.2.1.6834.5010.322628904903035357840500590726"
    tags = nbia_client.getDICOMTags(seriesUID)
    importantTags = [
        "Study Instance UID",
        "Series Instance UID",
        "SOP Instance UID",
        "Image Type",
        "Study ID",
        "Series Number",
        "Acquisition Number",
        "Instance Number",
        "Image Position (Patient)",
        "Image Orientation (Patient)",
        "Frame of Reference UID",
        "Position Reference Indicator",
        "Slice Location",
        "Samples per Pixel",
        "Rows",
        "Columns",
        "Pixel Spacing",
        "Study Date",
        "Series Date",
        "Modality",
        "Study Description",
        "Series Description",
        "Patient's Name",
        "Patient ID",
        "Patient's Birth Date",
        "Patient's Sex",
        "Patient's Age",
        "Instance Creation Date",
        "Instance Creation Time",
    ]
    print(seriesUID)
    all_names = [tag["name"] for tag in tags]
    for tag in importantTags:
        assert tag in all_names
