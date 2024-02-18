import pytest
from src.nbiatoolkit import NBIAClient
from tempfile import TemporaryDirectory
import os


@pytest.fixture
def nbia_client():
    return NBIAClient()


def test_downloadSeries(nbia_client):
    seriesList = nbia_client.getSeries(Collection="NSCLC-Radiomics")
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
