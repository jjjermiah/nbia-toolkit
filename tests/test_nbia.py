#####
# pytest -v -n 8

# To run only one of the tests:
# pytest -v -n 8 tests/test_nbia.py::test_getCollections

import pytest
from src.nbiatoolkit import NBIAClient
from tempfile import TemporaryDirectory
import os

@pytest.fixture(scope="session")
def nbia_client():
    nbia = NBIAClient()
    return nbia

@pytest.fixture(scope="session")
def nbia_client_bad_username():
    nbia = NBIAClient(username="bad_username", password="bad_password")
    return nbia


@pytest.fixture(scope="session")
def nbia_collections(nbia_client):
    collections = nbia_client.getCollections()
    return collections

@pytest.fixture(scope="session")
def nbia_patients(nbia_client, nbia_collections):
    patients = nbia_client.getPatients(
        Collection=nbia_collections[0])
    return patients

@pytest.fixture(scope="session")
def nbia_ModalityValues(nbia_client, nbia_collections):
    modalities = nbia_client.getModalityValues(
        Collection=nbia_collections[0])
    return modalities

@pytest.fixture(scope="session")
def nbia_patientsByCollectionAndModality(nbia_client, nbia_collections):
    patients = nbia_client.getPatientsByCollectionAndModality(
        Collection=nbia_collections[0], Modality = "CT")
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

def test_getPatientsByCollectionAndModality(nbia_patientsByCollectionAndModality):
    assert isinstance(nbia_patientsByCollectionAndModality, list)
    assert len(nbia_patientsByCollectionAndModality) > 0
    assert isinstance(nbia_patientsByCollectionAndModality[0], str)
    assert len(nbia_patientsByCollectionAndModality[0]) > 0

def test_getSeries(nbia_client, nbia_collections, nbia_patients):
    seriesList = nbia_client.getSeries(
        Collection=nbia_collections[0],
        PatientID=nbia_patients[0],
        Modality="CT"
    )
    assert seriesList is not None
    assert isinstance(seriesList, list)
    assert len(seriesList) > 0
    assert isinstance(seriesList[0], dict)
    
def test_fail_getSeries(nbia_client, nbia_collections, nbia_patients):
    with pytest.raises(Exception):
        seriesList = nbia_client.getSeries(
            Collection=nbia_collections[0],
            PatientID=nbia_patients[0],
            Modality="CT",
            SeriesInstanceUID="bad_series_uid"
        )
        assert seriesList is not None
        assert isinstance(seriesList, list)
        assert len(seriesList) > 0
        assert isinstance(seriesList[0], dict)
        


    # nbia_client.downloadSeries(

