import pytest
from nbiatoolkit import nbia

from src.nbiatoolkit import NBIAClient
from src.nbiatoolkit.auth import OAuth2
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


def test_tcga_studies(tcga_studies):

    assert isinstance(tcga_studies, list)
    assert len(tcga_studies) > 0
