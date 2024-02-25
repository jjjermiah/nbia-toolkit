from math import log
import pytest
from src.nbiatoolkit import NBIAClient
from src.nbiatoolkit.auth import OAuth2
from src.nbiatoolkit.utils import *
from src.nbiatoolkit.logger import setup_logger
import pandas as pd


@pytest.fixture(scope="session")
def nbia_client():
    nbia_client = NBIAClient(log_level="DEBUG")
    return nbia_client


@pytest.fixture(scope="session")
def nbia_client2():
    nbia_client = NBIAClient(log_level="DEBUG")
    return nbia_client


@pytest.fixture(scope="session")
def tcga_patients(nbia_client):

    tcga_patients = nbia_client.getPatients(Collection="TCGA-KIRC")

    return tcga_patients


def test_nbia_properties(nbia_client2):
    nbia_client = nbia_client2
    assert isinstance(nbia_client.OAuth_client, OAuth2)
    assert isinstance(nbia_client.headers, dict)
    assert "Authorization" in nbia_client.headers.keys()
    assert "Content-Type" in nbia_client.headers.keys()
    assert nbia_client.headers["Content-Type"] == "application/json"

    assert nbia_client.base_url == NBIA_BASE_URLS.NBIA

    assert nbia_client.logger is not None

    nbia_client.logger = setup_logger(
        name="NBIAClient", log_level="INFO", console_logging=True, log_file=None
    )

    assert nbia_client.return_type == "list"
    nbia_client.return_type = "dataframe"


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
