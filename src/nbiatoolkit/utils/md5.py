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
