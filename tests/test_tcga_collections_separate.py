from math import log
import pytest
from src.nbiatoolkit import NBIAClient
from src.nbiatoolkit.auth import OAuth2
from src.nbiatoolkit.utils import *
import pandas as pd


@pytest.fixture(scope="session")
def nbia_client():
    nbia_client = NBIAClient(log_level="DEBUG")
    return nbia_client


@pytest.fixture(scope="session")
def nbia_client_tobreak():
    nbia_client = NBIAClient(log_level="DEBUG")
    return nbia_client


@pytest.fixture(scope="session")
def tcga_collections(nbia_client):
    tcga_collections = nbia_client.getCollections(prefix="TCGA")
    tcga_collection_df = nbia_client.getCollections(
        prefix="TCGA", return_type="dataframe"
    )
    return (tcga_collection_df, tcga_collections)


@pytest.fixture(scope="session")
def nbia_context_manager():
    with NBIAClient(log_level="WARNING") as nbia_client:
        yield nbia_client


def test_nbia_properties(nbia_context_manager):
    assert isinstance(nbia_context_manager.OAuth_client, OAuth2)
    assert isinstance(nbia_context_manager.headers, dict)
    assert "Authorization" in nbia_context_manager.headers.keys()
    assert "Content-Type" in nbia_context_manager.headers.keys()
    assert nbia_context_manager.headers["Content-Type"] == "application/json"


def test_break(nbia_client_tobreak):
    assert nbia_client_tobreak.base_url == NBIA_BASE_URLS.NBIA
    nbia_client_tobreak.base_url = NBIA_BASE_URLS.NLST
    assert nbia_client_tobreak.base_url == NBIA_BASE_URLS.NLST


def test_getModalityValues(nbia_client, tcga_collections):
    tcga_collections_df, tcga_collections = tcga_collections
    modality_values = nbia_client.getModalityValues(
        Collection=tcga_collections[0]["Collection"]
    )
    assert isinstance(modality_values, list)
    assert len(modality_values) > 1

    modality_values_df = nbia_client.getModalityValues(
        Collection=tcga_collections[0]["Collection"], return_type="dataframe"
    )
    assert isinstance(modality_values_df, pd.DataFrame)
    assert "Modality" in modality_values_df.columns
    assert len(modality_values_df) > 1


def test_tcga_collection(tcga_collections):
    tcga_collections_df, tcga_collections1 = tcga_collections
    assert isinstance(tcga_collections1, list)
    assert len(tcga_collections1) > 1

    assert isinstance(tcga_collections_df, pd.DataFrame)
    assert "Collection" in tcga_collections_df.columns
    assert len(tcga_collections_df) > 1


def test_getCollectionPatientCount(nbia_client):
    patient_count = nbia_client.getCollectionPatientCount(prefix="TCGA-KIRC")
    assert isinstance(patient_count, list)
    assert len(patient_count) > 0


def test_getBodyPartCounts(nbia_client):
    body_part_counts = nbia_client.getBodyPartCounts(Collection="TCGA-KIRC")
    assert isinstance(body_part_counts, list)
    assert len(body_part_counts) > 0
