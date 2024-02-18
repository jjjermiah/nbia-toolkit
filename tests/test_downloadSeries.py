import pytest
from src.nbiatoolkit import NBIAClient
from tempfile import TemporaryDirectory
import os
import requests


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

    # assert len(dir) == 1
    # assert os.path.isdir(os.path.join(tempdir, dir[0]))

    # modality_dir = os.listdir(os.path.join(tempdir, dir[0]))
    # assert len(modality_dir) == 1
    # assert modality_dir[0] == "CT"
    # assert os.path.isdir(os.path.join(tempdir, dir[0], modality_dir[0]))

    # series_dir = os.listdir(os.path.join(tempdir, dir[0], modality_dir[0]))
    # assert len(series_dir) == 1
    # # only last 5 digits of SeriesInstanceUID are used
    # assert series_dir[0] == "{}-{}".format(
    #     seriesList[0]["SeriesNumber"], seriesList[0]["SeriesInstanceUID"][-5:]
    # )
    # assert os.path.isdir(os.path.join(tempdir, dir[0], modality_dir[0], series_dir[0]))

    # dicom_dir = os.listdir(
    #     os.path.join(tempdir, dir[0], modality_dir[0], series_dir[0])
    # )

    # assert len(dicom_dir) == int(seriesList[0]["ImageCount"])
    # for file in dicom_dir:
    #     assert file.endswith(".dcm")
    #     assert file[:-4].isdigit()
