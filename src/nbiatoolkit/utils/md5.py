import hashlib, os


# Define MD5HashMismatchError
class MD5HashMismatchError(Exception):
    pass


def calculateMD5(filepath: str) -> str:
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def validateMD5(seriesDir: str) -> bool:
    md5File = os.path.join(seriesDir, "md5hashes.csv")
    if not os.path.isfile(md5File):
        # "MD5 hash file not found in download directory."
        raise FileNotFoundError("MD5 hash file not found in download directory.")

    with open(md5File, "r") as f:
        lines = f.readlines()

    for line in lines[1:]:
        filepath = os.path.join(seriesDir, line.split(",")[0])
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File not found in seriesDir: {filepath}")

        md5hash = line.split(",")[1].strip().lower()
        md5 = calculateMD5(filepath)

        if md5 != md5hash:
            # f"MD5 hash mismatch for file: {filepath}"
            raise MD5HashMismatchError(f"MD5 hash mismatch for file: {filepath}")

    # delete the md5 file if all hashes match
    os.remove(md5File)
    return True


if __name__ == "__main__":
    import sys
    import io
    import os
    import zipfile
    from nbiatoolkit.utils.nbia_endpoints import NBIA_ENDPOINTS
    from nbiatoolkit import NBIAClient
    import requests
    from tempfile import TemporaryDirectory

    client = NBIAClient()
    series = "1.3.6.1.4.1.14519.5.2.1.6834.5010.189721824525842725510380467695"
    query_url = NBIA_ENDPOINTS.BASE_URL.value + NBIA_ENDPOINTS.DOWNLOAD_SERIES.value

    params = dict()
    params["SeriesInstanceUID"] = series

    response = requests.get(url=query_url, headers=client.api_headers, params=params)

    file = zipfile.ZipFile(io.BytesIO(response.content))

    tempDir_ = TemporaryDirectory()
    tempDir = tempDir_.name

    file.extractall(path=tempDir)

    try:
        validateMD5(tempDir)
        print("MD5 hashes validated successfully.")
    except AssertionError as e:
        print(f"Error validating MD5 hashes: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error validating MD5 hashes: {e}")
        sys.exit(1)
