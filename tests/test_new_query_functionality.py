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
def tcga_collections(nbia_client):
    tcga_collections = nbia_client.getCollections(prefix="TCGA")
    tcga_collection_df = nbia_client.getCollections(
        prefix="TCGA", return_type="dataframe"
    )
    return (tcga_collection_df, tcga_collections)


@pytest.fixture(scope="session")
def tcga_patients(nbia_client):

    tcga_patients = nbia_client.getPatients(Collection="TCGA-KIRC")

    return tcga_patients


@pytest.fixture(scope="session")
def nbia_patients_df(nbia_client: NBIAClient, tcga_patients):
    nbia_patients_df = nbia_client.getNewPatients(
        Collection="CMB-LCA", return_type="dataframe", Date="2022/12/06"
    )
    return nbia_patients_df


@pytest.fixture(scope="session")
def nbia_collections_by_colMoldality(nbia_client: NBIAClient, nbia_patients_df):
    nbia_collections_by_colMoldality = nbia_client.getPatientsByCollectionAndModality(
        Collection="TCGA-KIRC", Modality="MR"
    )
    return nbia_collections_by_colMoldality


def test_nbia_properties(nbia_client):
    assert isinstance(nbia_client.OAuth_client, OAuth2)
    assert isinstance(nbia_client.headers, dict)
    assert "Authorization" in nbia_client.headers.keys()
    assert "Content-Type" in nbia_client.headers.keys()
    assert nbia_client.headers["Content-Type"] == "application/json"

    assert nbia_client.base_url == NBIA_ENDPOINTS.NBIA
    nbia_client.base_url = NBIA_ENDPOINTS.NLST
    assert nbia_client.base_url == NBIA_ENDPOINTS.NLST

    assert nbia_client.logger is not None


def test_tcga_collection(tcga_collections):
    tcga_collections_df, tcga_collections1 = tcga_collections
    assert isinstance(tcga_collections1, list)
    assert len(tcga_collections1) > 1

    assert isinstance(tcga_collections_df, pd.DataFrame)
    assert "Collection" in tcga_collections_df.columns
    assert len(tcga_collections_df) > 1


def test_tcga_collection_description(nbia_client: NBIAClient):
    tcga_collection_description_df = nbia_client.getCollectionDescriptions(
        collectionName="TCGA-KIRC", return_type="dataframe"
    )
    tcga_collection_description = nbia_client.getCollectionDescriptions(
        collectionName="TCGA-KIRC"
    )

    assert isinstance(tcga_collection_description, list)
    assert isinstance(tcga_collection_description_df, pd.DataFrame)

    assert len(tcga_collection_description) == 1
    assert len(tcga_collection_description_df) == 1


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


def test_failed_getModalityValues(nbia_client):
    with pytest.raises(Exception) as e:
        # collection isntead of Collection
        nbia_client.getModalityValues(collection="TCGA")

    with pytest.raises(Exception) as e:
        # collection isntead of Collection
        nbia_client.getModalityValues(collection="TCGA", return_type="dataframe")


def test_getPatients(nbia_client, tcga_patients):

    assert isinstance(tcga_patients, list)
    assert len(tcga_patients) > 1


def test_getNewPatients(nbia_patients_df):

    assert isinstance(nbia_patients_df, pd.DataFrame)
    assert len(nbia_patients_df) > 1
    expected_cols: list[str] = [
        "PatientId",
        "PatientName",
        "PatientSex",
        "Collection",
        "Phantom",
        "SpeciesCode",
        "Species",
    ]


def test_failed_getNewPatients(nbia_client):
    with pytest.raises(Exception) as e:
        # collection isntead of Collection
        nbia_client.getNewPatients(collection="TCGA", Date="2022/12/06")

    with pytest.raises(Exception) as e:
        # collection isntead of Collection
        nbia_client.getNewPatients(
            collection="TCGA", return_type="dataframe", Date="2022/12/06"
        )


def test_nbia_collections_by_colMoldality(nbia_collections_by_colMoldality):
    assert isinstance(nbia_collections_by_colMoldality, list)
    assert len(nbia_collections_by_colMoldality) > 1
