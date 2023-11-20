from nbiatoolkit import NBIAClient
import requests
from pprint import pprint

client = NBIAClient(log_level="DEBUG")
# series = client.getSeries(Collection="4D-Lung")
# pprint(series[0])
# print(type(series[0]))
# print()

# series0 = series[0]['SeriesInstanceUID']
series0 = '1.3.6.1.4.1.14519.5.2.1.6834.5010.189721824525842725510380467695'
response = client.downloadSeries(
    SeriesInstanceUID = series0,
    downloadDir = "/home/bioinf/bhklab/jermiah/projects/NBIA-toolkit/resources")
# pprint(response)
