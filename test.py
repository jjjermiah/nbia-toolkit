# med-imagetools/src/med_imagetools/index.py

import pandas as pd
from pathlib import Path
import asyncio
from imgtools.dicom.crawl import Crawler

from nbiatoolkit.nbia import NBIAClient
from nbiatoolkit import NBIA_ENDPOINT
from nbiatoolkit.dicomtags.tags import generateFileDatasetFromTags


client = NBIAClient()

collections = client.getCollections()

for collection in collections:

    series = client.getSeries({'Collection': collection})

    n = 0
    for s in series:
        tags = asyncio.run(
            client.query_json(NBIA_ENDPOINT.GET_DICOM_TAGS.value, {"SeriesUID": s[0]["SeriesInstanceUID"]})
        )
        tags_df = pd.DataFrame(tags)

        ds = generateFileDatasetFromTags(tags_df)

        output_path = Path("temp_output")
        output_path.mkdir(parents=True, exist_ok=True)
        ds.save_as(output_path / f"{s[0]['SeriesInstanceUID']}.dcm")

        if n > 5:
            break

        n += 1

    crawler = Crawler(output_path)
    crawler.crawl()

    # CONVERT CRAWL CSV TO A GITHUB RELEASE

# med-imagetools/src/med_imagetools/query.py





