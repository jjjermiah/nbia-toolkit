import re, os, sys, shutil
import pydicom
import argparse

from pydicom.errors import InvalidDicomError

from .helper_functions import parseDICOMKeysFromFormat, sanitizeFileName, truncateUID

from typing import Optional

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


class DICOMSorter:
    def __init__(
        self,
        sourceDir: str,
        destinationDir: str,
        targetPattern: str = "%PatientName/%SeriesNumber-%SeriesInstanceUID/%InstanceNumber.dcm",
        truncateUID: bool = True,
        sanitizeFilename: bool = True,
    ):
        """
        Initialize the DICOMSorter with a target pattern.
        """
        self.targetPattern = targetPattern
        self.sourceDir = sourceDir
        self.destinationDir = destinationDir
        self.truncateUID = truncateUID
        self.sanitizeFilename = sanitizeFilename

    def generateFilePathFromDICOMAttributes(self, dataset: pydicom.FileDataset) -> str:
        """
        Generate a file path for the DICOM file by formatting DICOM attributes.
        """
        fmt, keys = parseDICOMKeysFromFormat(targetPattern=self.targetPattern)
        replacements: dict[str, str] = {}

        # Prepare the replacements dictionary with sanitized attribute values
        for key in keys:
            # Retrieve the attribute value if it exists or default to a placeholder string
            value = str(getattr(dataset, key, "Unknown" + key))

            value = (
                truncateUID(value)
                if key.endswith("UID") and self.truncateUID
                else value
            )

            replacements[key] = (
                sanitizeFileName(value) if self.sanitizeFilename else value
            )

        # Build the target path by interpolating the replacement values
        return fmt % replacements

    def sortSingleDICOMFile(
        self, filePath: str, option: str, overwrite: bool = False
    ) -> bool:
        assert option in ["copy", "move"], "Invalid option: symlink not implemented yet"

        try:
            dataset: pydicom.FileDataset = pydicom.dcmread(
                filePath, stop_before_pixels=True
            )
        except InvalidDicomError as e:
            print(f"Error reading file {filePath}: {e}")
            return False
        except TypeError as e:
            print(
                f"Error reading file {filePath}: is ``None`` or of an unsupported type."
            )
            return False

        name = self.generateFilePathFromDICOMAttributes(dataset)
        assert name is not None and isinstance(name, str)

        targetFilename = os.path.join(self.destinationDir, name)

        if os.path.exists(targetFilename) and not overwrite:
            print(f"Source File: {filePath}\n")
            print(f"File {targetFilename} already exists. ")
            raise ValueError(
                "Pattern is probably not unique or overwrite is set to False. Exiting."
            )

        os.makedirs(os.path.dirname(targetFilename), exist_ok=True)

        if option == "copy":
            shutil.copyfile(src=filePath, dst=targetFilename)
        elif option == "move":
            shutil.move(src=filePath, dst=targetFilename)
        else:
            raise ValueError(f"Invalid option: {option}")

        return True

    def sortDICOMFiles(
        self, option: str = "copy", overwrite: bool = False, nParallel: int = 1
    ) -> bool:
        dicom_file_paths = self._get_dicom_files()
        result = []
        print("Running with {} parallel threads".format(nParallel))

        with ThreadPoolExecutor(max_workers=nParallel) as executor:
            futures = [
                executor.submit(self.sortSingleDICOMFile, filePath, option, overwrite)
                for filePath in dicom_file_paths
            ]

            for future in tqdm(as_completed(futures), total=len(futures)):
                result.append(future.result())

        return all(result)

    def _get_dicom_files(self) -> "list[str]":
        dicom_file_paths = []
        # Iterate over all files in the source directory
        for root, dirs, files in os.walk(self.sourceDir):
            for f in files:
                dicom_file_paths.append(os.path.join(root, f)) if f.endswith(
                    ".dcm"
                ) else None

        return dicom_file_paths


# Create command line interface

# Given a source directory, destination directory, and target pattern, sort DICOM files
# into the destination directory according to the target pattern.
# The target pattern is a string with placeholders matching '%<DICOMKey>'.


def DICOMSorter_cli():
    parser = argparse.ArgumentParser(
        description="Sort DICOM files into destination directory according to target pattern."
    )

    parser.add_argument(
        "sourceDir",
        metavar="sourceDir",
        type=str,
        help="The source directory containing DICOM files.",
    )

    parser.add_argument(
        "destinationDir",
        metavar="destinationDir",
        type=str,
        help="The destination directory to sort DICOM files into.",
    )

    # Default is %%PatientName/%%SeriesNumber-%%SeriesInstanceUID/%%InstanceNumber.dcm
    parser.add_argument(
        "--targetPattern",
        dest="targetPattern",
        default="%PatientName/%SeriesNumber-%SeriesInstanceUID/%InstanceNumber.dcm",
        type=str,
        help="The target pattern for sorting DICOM files. Default is %%PatientName/%%SeriesNumber-%%SeriesInstanceUID/%%InstanceNumber.dcm.",
    )

    parser.add_argument(
        "--truncateUID",
        dest="truncateUID",
        action="store_true",
        default=True,
        help="Truncate the UID to the last n characters (includes periods & underscores). Default is True.",
    )

    parser.add_argument(
        "--sanitizeFilename",
        dest="sanitizeFilename",
        action="store_true",
        help="Sanitize the file name by replacing potentially dangerous characters. Default is True.",
    )

    parser.add_argument(
        "--overwrite",
        dest="overwrite",
        action="store_true",
        help="Overwrite existing files. Default is False.",
    )

    parser.add_argument(
        "--nParallel",
        dest="nParallel",
        action="store",
        type=int,
        help="Number of parallel threads. Default is 1.",
    )

    parser.set_defaults(truncateUID=True)
    parser.set_defaults(sanitizeFilename=True)
    parser.set_defaults(overwrite=False)
    parser.set_defaults(nParallel=1)

    args = parser.parse_args()

    sorter = DICOMSorter(
        sourceDir=args.sourceDir,
        destinationDir=args.destinationDir,
        targetPattern=args.targetPattern,
        truncateUID=args.truncateUID,
        sanitizeFilename=args.sanitizeFilename,
    )

    sorter.sortDICOMFiles(
        option="copy", overwrite=args.overwrite, nParallel=int(args.nParallel)
    )
