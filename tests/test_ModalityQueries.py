import pytest

from src.nbiatoolkit import NBIAClient
from src.nbiatoolkit.utils import *
import pandas as pd


@pytest.fixture(scope="session")
def nbia_client():
    return NBIAClient()


def test_getModalityValues(nbia_client: NBIAClient):
    modality_values = nbia_client.getModalityValues()

    assert isinstance(modality_values, list)
    assert len(modality_values) > 0
    assert isinstance(modality_values[0], dict)
    assert len(modality_values[0].keys()) == 1

    assert isinstance(modality_values[0]["Modality"], str)


def test_getModalityValuesCounts(nbia_client: NBIAClient):
    modality_values_counts = nbia_client.getModalityValues(Counts=True)

    assert isinstance(modality_values_counts, list)
    assert len(modality_values_counts) > 0
    assert isinstance(modality_values_counts[0], dict)
    assert len(modality_values_counts[0].keys()) == 2
