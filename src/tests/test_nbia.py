#####
# pytest -v -n 8
import pytest
from ..nbia import NBIAClient

@pytest.fixture(scope="session")
def nbia_client():
    nbia = NBIAClient()
    return nbia

@pytest.fixture(scope="session")
def nbia_client_bad_username():
    nbia = NBIAClient(username="bad_username", password="bad_password")
    return nbia

def test_nbiaclient_access_token(nbia_client):
    assert nbia_client.api_headers is not None
    
def test_getCollections(nbia_client):
    collections = nbia_client.getCollections()
    assert isinstance(collections, list)
    assert len(collections) > 0
    
def test_getBodyPartCounts_all(nbia_client):
    bodyparts = nbia_client.getBodyPartCounts()
    assert isinstance(bodyparts, list)
    assert len(bodyparts) > 0
    assert "BodyPartExamined" in bodyparts[0]    
    assert "Count" in bodyparts[0]
    assert int(bodyparts[0]["Count"]) > 0
    
def test_getBodyPartCounts_4DLung(nbia_client):
    bodyparts = nbia_client.getBodyPartCounts(collection="4D-Lung")
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
    
def test_getPatients(nbia_client):
    patientList = nbia_client.getPatients("LIDC-IDRI", "CT")
    assert isinstance(patientList, list)
    assert len(patientList) > 0
    assert isinstance(patientList[0], str)
    assert len(patientList[0]) > 0
    