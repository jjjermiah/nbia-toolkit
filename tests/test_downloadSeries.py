import pytest
from sqlalchemy import over
from src.nbiatoolkit import NBIAClient, downloadSingleSeries
from tempfile import TemporaryDirectory
import os


@pytest.fixture
def nbia_client():
    return NBIAClient()


@pytest.fixture
def series_list(nbia_client):
    return nbia_client.getSeries(Collection="NSCLC-Radiomics")


def test_downloadSeries(nbia_client, series_list):
    seriesList = series_list
    filePattern = (
        "%PatientID/%Modality-%SeriesNumber-%SeriesInstanceUID/%InstanceNumber.dcm"
    )
    # create a temporary directory

    with TemporaryDirectory() as tempdir:

        nbia_client.downloadSeries(
            SeriesInstanceUID=seriesList[0]["SeriesInstanceUID"],
            downloadDir=tempdir,
            filePattern=filePattern,
        )
        dir = os.listdir(tempdir)

        assert len(dir) == 1
        assert os.path.isdir(os.path.join(tempdir, dir[0]))

        modality_dir = os.listdir(os.path.join(tempdir, dir[0]))
        assert len(modality_dir) == 1
        assert modality_dir[0].startswith("CT")
        assert os.path.isdir(os.path.join(tempdir, dir[0], modality_dir[0]))


def test_downloadSingleSeries(nbia_client, series_list):
    seriesList = series_list
    filePattern = (
        "%PatientID/%Modality-%SeriesNumber-%SeriesInstanceUID/%InstanceNumber.dcm"
    )
    # create a temporary directory

    with TemporaryDirectory() as tempdir:

        downloadSingleSeries(
            SeriesInstanceUID=seriesList[0]["SeriesInstanceUID"],
            downloadDir=tempdir,
            filePattern=filePattern,
            overwrite=True,
            api_headers=nbia_client.headers,
            base_url=nbia_client.base_url,
            log=nbia_client.logger,
        )
        dir = os.listdir(tempdir)

        assert len(dir) == 1
        assert os.path.isdir(os.path.join(tempdir, dir[0]))

        modality_dir = os.listdir(os.path.join(tempdir, dir[0]))
        assert len(modality_dir) == 1
        assert modality_dir[0].startswith("CT")
        assert os.path.isdir(os.path.join(tempdir, dir[0], modality_dir[0]))
