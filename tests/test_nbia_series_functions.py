import pytest

from src.nbiatoolkit import NBIAClient
from src.nbiatoolkit.utils import *
import pandas as pd


@pytest.fixture(scope="session")
def nbia_client():
    nbia_client = NBIAClient()
    return nbia_client


@pytest.fixture(scope="session")
def tcga_series(nbia_client):
    tcga_series = nbia_client.getSeries(
        Collection="TCGA-KIRC", PatientID="TCGA-BP-4989"
    )
    return tcga_series


@pytest.fixture(scope="session")
def tcga_studies(nbia_client):
    tcga_studies = nbia_client.getStudies(
        Collection="TCGA-KIRC", PatientID="TCGA-BP-4989"
    )
    return tcga_studies


@pytest.fixture(scope="session")
def nbia_patients_df(nbia_client: NBIAClient):
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


def test_tcga_studies(tcga_studies):

    assert isinstance(tcga_studies, list)
    assert len(tcga_studies) > 0


def test_failed_getNewPatients(nbia_client):
    with pytest.raises(Exception) as e:
        # collection isntead of Collection
        nbia_client.getNewPatients(collection="TCGA", Date="2022/12/06")

    with pytest.raises(Exception) as e:
        # collection isntead of Collection
        nbia_client.getNewPatients(
            collection="TCGA", return_type="dataframe", Date="2022/12/06"
        )


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


def test_nbia_collections_by_colMoldality(nbia_collections_by_colMoldality):
    assert isinstance(nbia_collections_by_colMoldality, list)
    assert len(nbia_collections_by_colMoldality) > 1
