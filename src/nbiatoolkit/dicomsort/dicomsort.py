# import re, os, sys, shutil
# import pydicom
# import argparse


# from typing import Optional

# from tqdm import tqdm
import pydicom
from pydicom.errors import InvalidDicomError
import os
import glob
import shutil
from .helper_functions import parseDICOMKeysFromFormat, sanitizeFileName, _truncateUID
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_dicom_files(sourceDir) -> list[str]:
    return [
        file
        for file in glob.glob(f"{sourceDir}/**/*.dcm", recursive=True)
        if os.path.isfile(file)
    ]


def read_in_dicom_file(filePath: str) -> pydicom.FileDataset:
    if not os.path.isfile(filePath):
        raise ValueError(f"The file {filePath} does not exist.")
    try:
        dataset: pydicom.FileDataset = pydicom.dcmread(
            filePath, stop_before_pixels=True
        )
        return dataset
    except InvalidDicomError as e:
        raise InvalidDicomError(f"Error reading file {filePath}: {e}")
    except Exception as e:
        raise e


def generateFilePathFromDICOMAttributes(
    dataset: pydicom.FileDataset,
    targetPattern: str,
    truncateUID: bool,
    sanitizeFilename: bool,
) -> str:
    """
    Generate a file path for the DICOM file by formatting DICOM attributes.
    """
    fmt: str
    keys: list[str]
    fmt, keys = parseDICOMKeysFromFormat(targetPattern=targetPattern)

    replacements: dict[str, str] = {}

    for key in keys:
        # Retrieve the attribute value if it exists or default to a placeholder string
        value = str(getattr(dataset, key, "Unknown" + key))

        value = (
            _truncateUID(uid=value, lastDigits=5)
            if key.endswith("UID") and truncateUID
            else value
        )

        replacements[key] = sanitizeFileName(value) if sanitizeFilename else value

    # Build the target path by interpolating the replacement values
    return fmt % replacements


def sortSingleDICOMFile(
    filePath: str,
    shutil_option: str,
    overwrite: bool,
    destinationDir: str,
    targetPattern: str,
    truncateUID: bool,
    sanitizeFilename: bool,
) -> bool:
    assert shutil_option in [
        "copy",
        "move",
    ], "Invalid shutil_option symlink not implemented yet"

    dataset: pydicom.FileDataset = read_in_dicom_file(filePath)

    if dataset is None:
        return False

    name = generateFilePathFromDICOMAttributes(
        dataset, targetPattern, truncateUID, sanitizeFilename
    )

    assert name is not None and isinstance(name, str)

    targetFilename = os.path.join(destinationDir, name)

    if os.path.exists(targetFilename) and not overwrite:
        print(f"Source File: {filePath}\n")
        print(f"File {targetFilename} already exists. ")
        raise ValueError(
            "Pattern is probably not unique or overwrite is set to False. Exiting."
        )

    os.makedirs(os.path.dirname(targetFilename), exist_ok=True)

    if shutil_option == "copy":
        shutil.copyfile(src=filePath, dst=targetFilename)
    elif shutil_option == "move":
        shutil.move(src=filePath, dst=targetFilename)
    else:
        raise ValueError(f"Invalid option: {shutil_option}")

    return True


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
        self.targetPattern = targetPattern
        self.sourceDir = sourceDir
        self.destinationDir = destinationDir
        self.truncateUID = truncateUID
        self.sanitizeFilename = sanitizeFilename

    def sortDICOMFiles(
        self,
        shutil_option: str = "copy",
        overwrite: bool = False,
        n_parallel: int = 1,
        progressbar=True,
    ) -> bool:
        # get the list of dicom files
        dicom_file_paths = get_dicom_files(self.sourceDir)

        if n_parallel == 1:
            for path in dicom_file_paths:
                if not sortSingleDICOMFile(
                    filePath=path,
                    shutil_option=shutil_option,
                    overwrite=overwrite,
                    destinationDir=self.destinationDir,
                    targetPattern=self.targetPattern,
                    truncateUID=self.truncateUID,
                    sanitizeFilename=self.sanitizeFilename,
                ):
                    return False  # If any errors occurred during sorting, return False
        else:
            with ThreadPoolExecutor(max_workers=n_parallel) as executor:
                futures = [
                    executor.submit(
                        sortSingleDICOMFile,
                        filePath=path,
                        shutil_option=shutil_option,
                        overwrite=overwrite,
                        destinationDir=self.destinationDir,
                        targetPattern=self.targetPattern,
                        truncateUID=self.truncateUID,
                        sanitizeFilename=self.sanitizeFilename,
                    )
                    for path in dicom_file_paths
                ]

                if progressbar:
                    futures = tqdm(
                        as_completed(futures),
                        total=len(futures),
                        ncols=100,
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} Files Processed",
                    )

                for future in futures:
                    if not future.result():
                        return (
                            False  # If any errors occurred during sorting, return False
                        )

        return True  # If no errors, return True


# Removed sortSingleDICOMFile and generateFilePathFromDICOMAttributes methods here.


# class DICOMSorter:
#     def __init__(
#         self,
#         sourceDir: str,
#         destinationDir: str,
#         targetPattern: str = "%PatientName/%SeriesNumber-%SeriesInstanceUID/%InstanceNumber.dcm",
#         truncateUID: bool = True,
#         sanitizeFilename: bool = True,
#     ):
#         """
#         Initialize the DICOMSorter with a target pattern.
#         """
#         self.targetPattern = targetPattern
#         self.sourceDir = sourceDir
#         self.destinationDir = destinationDir
#         self.truncateUID = truncateUID
#         self.sanitizeFilename = sanitizeFilename

#     def generateFilePathFromDICOMAttributes(self, dataset: pydicom.FileDataset) -> str:
#         """
#         Generate a file path for the DICOM file by formatting DICOM attributes.
#         """
#         fmt, keys = parseDICOMKeysFromFormat(targetPattern=self.targetPattern)
#         replacements: dict[str, str] = {}

#         # Prepare the replacements dictionary with sanitized attribute values
#         for key in keys:
#             # Retrieve the attribute value if it exists or default to a placeholder string
#             value = str(getattr(dataset, key, "Unknown" + key))

#             value = (
#                 truncateUID(value)
#                 if key.endswith("UID") and self.truncateUID
#                 else value
#             )

#             replacements[key] = (
#                 sanitizeFileName(value) if self.sanitizeFilename else value
#             )

#         # Build the target path by interpolating the replacement values
#         return fmt % replacements

#     def sortSingleDICOMFile(
#         self, filePath: str, option: str, overwrite: bool = False
#     ) -> bool:
#         assert option in ["copy", "move"], "Invalid option: symlink not implemented yet"

#         try:
#             dataset: pydicom.FileDataset = pydicom.dcmread(
#                 filePath, stop_before_pixels=True
#             )
#         except InvalidDicomError as e:
#             print(f"Error reading file {filePath}: {e}")
#             return False
#         except TypeError as e:
#             print(
#                 f"Error reading file {filePath}: is ``None`` or of an unsupported type."
#             )
#             return False

#         name = self.generateFilePathFromDICOMAttributes(dataset)
#         assert name is not None and isinstance(name, str)

#         targetFilename = os.path.join(self.destinationDir, name)

#         if os.path.exists(targetFilename) and not overwrite:
#             print(f"Source File: {filePath}\n")
#             print(f"File {targetFilename} already exists. ")
#             raise ValueError(
#                 "Pattern is probably not unique or overwrite is set to False. Exiting."
#             )

#         os.makedirs(os.path.dirname(targetFilename), exist_ok=True)

#         if option == "copy":
#             shutil.copyfile(src=filePath, dst=targetFilename)
#         elif option == "move":
#             shutil.move(src=filePath, dst=targetFilename)
#         else:
#             raise ValueError(f"Invalid option: {option}")

#         return True


# def sortDICOMFiles(
#     self, option: str = "copy", overwrite: bool = False, nParallel: int = 1
# ) -> bool:
#     dicom_file_paths = _get_dicom_files(self.sourceDir)
#     result = []
#     print("Running with {} parallel threads".format(nParallel))

#     with ThreadPoolExecutor(max_workers=nParallel) as executor:
#         futures = [
#             executor.submit(self.sortSingleDICOMFile, filePath, option, overwrite)
#             for filePath in dicom_file_paths
#         ]

#         for future in tqdm(as_completed(futures), total=len(futures)):
#             result.append(future.result())

#     return all(result)

# def _get_dicom_files(sourceDir) -> "list[str]":
#     dicom_file_paths = []
#     # Iterate over all files in the source directory
#     for root, dirs, files in os.walk(sourceDir):
#         for f in files:
#             dicom_file_paths.append(os.path.join(root, f)) if f.endswith(
#                 ".dcm"
#             ) else None
#     return dicom_file_paths

# def _read_in_dicom_file(filePath: str) -> Optional[pydicom.FileDataset]:
#     try:
#         dataset: pydicom.FileDataset = pydicom.dcmread(
#             filePath, stop_before_pixels=True
#         )
#         return dataset
#     except InvalidDicomError as e:
#         print(f"Error reading file {filePath}: {e}")
#         return None
#     except TypeError as e:
#         print(f"Error reading file {filePath}: is ``None`` or of an unsupported type.")
#         return None


# sourceDir = "/Users/bhklab/Documents/GitHub/NBIA-toolkit/NBIA-Download"
# files = _get_dicom_files(sourceDir=sourceDir)
# dcm_list = []
# for file in files:
#     dcm = _read_in_dicom_file(file)
#     dcm_list.append(dcm)
