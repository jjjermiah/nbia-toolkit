import re, os, sys, shutil
import pydicom

from pydicom.filereader import InvalidDicomError

from .helper_functions import parseDICOMKeysFromFormat, sanitizeFileName, truncateUID


class DICOMSorter:
    def __init__(
        self,
        sourceDir: str,
        destinationDir: str,
        targetPattern: str = None,
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

    def generateFilePathFromDICOMAttributes(
        self, dataset: pydicom.dataset.FileDataset
    ) -> str:
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
            dataset = pydicom.dcmread(filePath, stop_before_pixels=True)
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
            sys.exit(
                "Pattern is probably not unique or overwrite is set to False. Exiting."
            )

        os.makedirs(os.path.dirname(targetFilename), exist_ok=True)

        match option:
            case "copy":
                shutil.copyfile(src=filePath, dst=targetFilename)
            case "move":
                shutil.move(src=filePath, dst=targetFilename)

        return True

    def sortDICOMFiles(self, option: str = "copy", overwrite: bool = False) -> bool:
        dicom_file_paths = self._get_dicom_files()

        results = [
            self.sortSingleDICOMFile(file, option, overwrite)
            for file in dicom_file_paths
        ]

        return all(results)

    def _get_dicom_files(self) -> list[str]:
        dicom_file_paths = []
        # Iterate over all files in the source directory
        for root, dirs, files in os.walk(self.sourceDir):
            for f in files:
                dicom_file_paths.append(os.path.join(root, f)) if f.endswith(
                    ".dcm"
                ) else None

        return dicom_file_paths


# Test case
# if __name__ == "__main__":

# sorter = DICOMSorter(
#     sourceDir = sourceDir,
#     destinationDir=destinationDir,
#     targetPattern=pattern,
#     truncateUID=True,
#     sanitizeFilename=True,
#     overwrite=True
#     )

# sorter.sortDICOMFiles(option="move")
