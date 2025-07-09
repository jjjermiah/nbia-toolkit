# med-imagetools/src/med_imagetools/index.py

import pandas as pd
from pathlib import Path
import asyncio
from imgtools.dicom.crawl import Crawler

from nbiatoolkit.nbia import NBIAClient
from nbiatoolkit import NBIA_ENDPOINT
from nbiatoolkit.dicomtags.tags import generateFileDatasetFromTags
from tqdm import tqdm
from glob import glob
from imgtools.dicom.dicom_metadata import extract_metadata
from pydicom import dcmread

import os
import pydicom

def get_series_instance_uids(dicom_dir):
    """Scan a directory for DICOM files and extract unique SeriesInstanceUIDs."""
    series_uids = set()

    for root, _, files in os.walk(dicom_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                ds = pydicom.dcmread(filepath, stop_before_pixels=True, force=True)
                if 'SeriesInstanceUID' in ds:
                    series_uids.add(ds.SeriesInstanceUID)
            except Exception as e:
                # Optional: print or log file-level errors
                pass

    return sorted(series_uids)

client = NBIAClient()

# collections = client.getCollections()
collections = ["4D-Lung"]

ref_path = "/Users/declankorda/BKHLAB-Internship-Stuff/med-imagetools/data/4D-Lung"

uids = get_series_instance_uids(ref_path)



for collection in collections:

    series = client.getSeries({'Collection': collection})

    n = 0

    for s in series:
        output_path = Path("temp_output")
        is_struct = False
        if s['SeriesInstanceUID'] not in uids:
            continue
        if s["Modality"] not in ["CT", "PT", "MR"]:
            is_struct = True
            sop_uid = client.getSOPIDs(s)
            for key in sop_uid:
                # blehh
                sop_uid = sop_uid[key][0]["SOPInstanceUID"]
            series_uid = s["SeriesInstanceUID"]
            file = asyncio.run(
                client.query_bytes(NBIA_ENDPOINT.DOWNLOAD_IMAGE.value, {"SeriesInstanceUID": series_uid, "SOPInstanceUID": sop_uid})
            )
            #tags = extract_metadata(file)
            ds = dcmread(file, stop_before_pixels=True, force=True)
        else: 
            tags = asyncio.run(
                client.query_json(NBIA_ENDPOINT.GET_DICOM_TAGS.value, {"SeriesUID": s["SeriesInstanceUID"]})
            )
            tags_df = pd.DataFrame(tags)
            ds = generateFileDatasetFromTags(tags_df)
        

        # add header to file before trying to save
        output_path = Path("temp_output")
        output_path.mkdir(parents=True, exist_ok=True)
        #print(f"\nfor {ds.SeriesInstanceUID} ({ds.Modality}):\n")
        #print(ds.get("FrameOfReferenceUID", "Missing"))
        #print(ds[0x00200052] if 0x00200052 in ds else "Tag not in dataset")
        ds.save_as(output_path / f"{s['SeriesInstanceUID']}.dcm", enforce_file_format=False)
        if n > 50:
            pass
            #break

        n += 1

    crawler = Crawler(output_path, force=True)
    crawler.crawl()

    # CONVERT CRAWL CSV TO A GITHUB RELEASE

# med-imagetools/src/med_imagetools/query.py