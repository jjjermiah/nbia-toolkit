from nbiatoolkit import NBIAClient
import requests
from pprint import pprint

client = NBIAClient(log_level="INFO")

# response = client.getPatients(collection="LIDC-IDRI", modality="CT")

# pprint(response[0:5])


response = client.getPatients(collection="LIDC-IDRI", modality="MRI")

pprint(response[0:5])
