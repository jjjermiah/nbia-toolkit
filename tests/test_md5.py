import os
from nbiatoolkit.utils.md5 import validateMD5, calculateMD5, MD5HashMismatchError
from nbiatoolkit.utils.nbia_endpoints import NBIA_ENDPOINTS
import requests
import pytest
from tempfile import TemporaryDirectory
import hashlib, os

def test_validateMD5_file_not_found():
    # Test case for when the MD5 hash file is not found
    seriesDir = "/path/to/seriesDir"
    with pytest.raises(FileNotFoundError):
        validateMD5(seriesDir)

# Test case for when a file mentioned in the MD5 hash file
# is not found in the seriesDir
def test_validateMD5_file_not_found_in_seriesDir():
    with TemporaryDirectory() as tempDir:
        testFile1 = os.path.join(tempDir, "file1.txt")
        with open(testFile1, "w") as f:
            f.write("This is some content")

        testFile2 = os.path.join(tempDir, "file2.txt")
        with open(testFile2, "w") as f:
            f.write("This is some other content")

        md5File = os.path.join(tempDir, "md5hashes.csv")

        # write to md5File with md5 hashes for testFile1 and testFile2
        with open(md5File, "w") as f:
            f.write(f"{testFile1},{calculateMD5(testFile1)}\n")
            f.write(f"{testFile2},{calculateMD5(testFile2)}\n")

        # delete testFile2
        os.remove(testFile2)

        with pytest.raises(FileNotFoundError):
            validateMD5(tempDir)

# Test case for when the calculated MD5 hash does not match
# the expected MD5 hash
def test_validateMD5_md5_hash_mismatch():
    with TemporaryDirectory() as tempDir:
        testFile1 = os.path.join(tempDir, "file1.txt")
        with open(testFile1, "w") as f:
            f.write("This is some content")

        testFile2 = os.path.join(tempDir, "file2.txt")
        with open(testFile2, "w") as f:
            f.write("This is some other content")

        md5File = os.path.join(tempDir, "md5hashes.csv")

        # write to md5File with md5 hashes for testFile1 and testFile2
        with open(md5File, "w") as f:
            f.write(f"{testFile1},{calculateMD5(testFile1)}\n")
            f.write(f"{testFile2},{calculateMD5(testFile2)}\n")

        # modify testFile2
        with open(testFile2, "w") as f:
            f.write("This is some other content.")

        with pytest.raises(MD5HashMismatchError):
            validateMD5(tempDir)

def test_validateMD5_all_hashes_match():
    with TemporaryDirectory() as tempDir:
        testFile1 = os.path.join(tempDir, "file1.txt")
        with open(testFile1, "w") as f:
            f.write("This is some content")

        testFile2 = os.path.join(tempDir, "file2.txt")
        with open(testFile2, "w") as f:
            f.write("This is some other content")

        md5File = os.path.join(tempDir, "md5hashes.csv")

        # write to md5File with md5 hashes for testFile1 and testFile2
        with open(md5File, "w") as f:
            f.write(f"{testFile1},{calculateMD5(testFile1)}\n")
            f.write(f"{testFile2},{calculateMD5(testFile2)}\n")

        assert validateMD5(tempDir)
        assert not os.path.isfile(md5File)

