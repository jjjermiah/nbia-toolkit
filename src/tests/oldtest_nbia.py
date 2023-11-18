## test_nbia.py

import pytest
from ..nbia import NBIAClient
import pandas as pd

@pytest.fixture(scope="session")
def nbia_client():
    nbia = NBIAClient()
    return nbia

@pytest.fixture(scope="session")
def nbia_client_bad_username():
    nbia = NBIAClient(username="bad_username", password="bad_password")
    return nbia

@pytest.fixture(scope="session")
def nbia_client_collections(nbia_client):
    nbia_client.getCollections()
    return nbia_client

def test_nbiaclient_access_token(nbia_client):
    assert nbia_client.access_token is not None

def test_nbia_getCollections(nbia_client_collections):
    collections = nbia_client_collections._collections
    assert isinstance(collections, pd.DataFrame)
    assert collections.shape[0] > 0
    assert collections.shape[1] == 1
    assert collections.columns[0] == 'Collection'

def test_nbia_getCollections_again(nbia_client_collections):
    collections = nbia_client_collections.getCollections()
    assert isinstance(collections, pd.DataFrame)
    assert collections.shape[0] > 0
    assert collections.shape[1] == 1
    assert collections.columns[0] == 'Collection'
    
def test_nbia_getCollectionDescription(nbia_client_collections):
    collectionName = '4D-Lung'
    collectionDescription = nbia_client_collections.getCollectionDescription(collectionName)
    # assert collectionDescriptions is a string and is not empty
    assert isinstance(collectionDescription, str)
    assert len(collectionDescription) > 0

def test_nbia_getCollectionDescription_bad_collection(nbia_client_collections, capsys):
    collectionName = 'bad_collection_testcase'
    collectionDescription = nbia_client_collections.getCollectionDescription(collectionName)
    captured = capsys.readouterr()
    # should be "Collection name {collectionName} does not exist."
    assert captured.out == \
        f"Collection name {collectionName} is not in the list of collections available. Please check the spelling or if this collection is restricted to authenticated users.\n"

def test_nbia_getBodyPartCounts(nbia_client):
    bodyPartCounts = nbia_client.getBodyPartCounts()
    assert isinstance(bodyPartCounts, pd.DataFrame)
    assert bodyPartCounts.shape[0] > 0
    assert bodyPartCounts.shape[1] == 2
    assert bodyPartCounts.columns[0] == 'BodyPart'
    assert bodyPartCounts.columns[1] == 'count'

