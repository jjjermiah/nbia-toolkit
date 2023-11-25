from nbiatoolkit import NBIAClient
import requests
from pprint import pprint
import multiprocessing as mp
from tqdm import tqdm
from tcia_utils import nbia
import logging
USERNAME = "sejinkim"
PASSWORD = "q6mJyLD8cPeGTwg!"


client = NBIAClient(
    username=USERNAME, 
    password=PASSWORD,
    log_level="DEBUG")

# series = client.getSeries(Collection="RADCURE")

# seriesList = [_["SeriesInstanceUID"] for _ in series]

series_one = "1.3.6.1.4.1.14519.5.2.1.245877810326980920641905130135164701440"

client.downloadSeries(
    SeriesInstanceUID=series_one, 
    downloadDir="./data/rawdata",
    filePattern = '%PatientName/%StudyDescription-%StudyDate/%SeriesNumber-%SeriesDescription-%SeriesInstanceUID/%InstanceNumber.dcm',
    overwrite = True
    )



# def download(series) -> bool:
#     response = client.downloadSeries(
#         SeriesInstanceUID = series,
#         downloadDir = "./rawdata2")
#     return response

# download(seriesList[0])


# # if (True):
# #     # iterate through each series and download
# #     # print out the progressbar
# #     with mp.Pool(processes=30) as pool:
# #         for _ in tqdm(pool.imap_unordered(download, seriesList), total=len(seriesList)):
# #             pass
# # else:
#     _log = logging.getLogger(__name__)
#     for handler in logging.root.handlers[:]:
#         logging.root.removeHandler(handler)

#     USERNAME = "sejinkim"
#     PASSWORD = "q6mJyLD8cPeGTwg!"
#     nbia.getToken(user=USERNAME, pw=PASSWORD)

#     collection_name = "RADCURE"
#     metadata = nbia.getSeries(collection = collection_name, format = "df", api_url = "restricted")
    
#     nbia.downloadSeries(series_data = seriesList, path = "/home/bioinf/bhklab/jermiah/projects/rawdata", input_type = "list",  api_url = "restricted")
# # with mp.Pool(processes=30) as pool:
# #     for _ in tqdm(pool.imap_unordered(download, seriesList), total=len(seriesList)):
# #         pass
# # python dicomsort.py -u /home/bioinf/bhklab/jermiah/projects/rawdata /home/bioinf/bhklab/jermiah/projects/NBIA-toolkit/resources/rawdata/%PatientID/%StudyDate-%StudyID-%StudyDescription-%StudyInstanceUID/%SeriesNumber-%SeriesDescription-%SeriesIntanceUID/%InstanceNumber-%SOPInstanceUID.dcm


    