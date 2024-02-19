import io
from .nbia import NBIAClient, __version__
from .dicomsort import DICOMSorter

import argparse
import sys
import threading
import sys
import subprocess

# import from typing libraries
from typing import List, Dict, Tuple, Union, Optional, Any

done_event = threading.Event()
query: str
output: io.TextIOWrapper | None = None


def version():
    f = """
        _   ______  _______  ______            ____   _ __
       / | / / __ )/  _/   |/_  __/___  ____  / / /__(_) /_
      /  |/ / __  |/ // /| | / / / __ \/ __ \/ / //_/ / __/
     / /|  / /_/ // // ___ |/ / / /_/ / /_/ / / ,< / / /_
    /_/ |_/_____/___/_/  |_/_/  \____/\____/_/_/|_/_/\__/
    """
    print(f)
    print("Version: {}".format(__version__))

    # print all available command line tools:
    print("\nAvailable CLI tools: \n")

    # run each command with -h to see the available options
    commands = [
        "getCollections",
        "getBodyPartCounts",
        "getPatients",
        "getNewPatients",
        "getStudies",
        "getSeries",
        "getNewSeries",
        # "downloadSingleSeries",
        # "dicomsort",
    ]
    for command in commands:
        result = subprocess.run([command, "-h"], capture_output=True, text=True)
        output_lines = result.stdout.splitlines()
        # print out every line from the output until theres a line that contains "usage" in it
        for line in output_lines:
            if "NBIAToolkit" in line:
                break
            print(line[7:])

    return


def _initialize_parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)

    # create an argparse group called "Credentials" to hold the username and password arguments
    credentials = p.add_argument_group(
        title="authentication parameters",
        description="The username and password for the NBIA API if querying restricted datasets, defaults to the NBIA Guest Account",
    )

    credentials.add_argument(
        "-u",
        "--username",
        action="store",
        type=str,
        default="nbia_guest",  # help="Username for the NBIA API (default: nbia_guest)"
    )

    credentials.add_argument(
        "-pw",
        "--password",
        action="store",
        type=str,
        default="",  # help="Password for the NBIA API (default: '')"
    )

    # make the credentials group show up first
    p._action_groups.insert(0, p._action_groups.pop())

    return p


def _add_extra_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    parser.add_argument(
        "-o",
        "--output",
        dest="outputfile",
        action="store",
        type=argparse.FileType("w", encoding="UTF-8"),
        help="Output file (tsv works best)",
    )

    parser.add_argument(
        "--version", "-v", action="store_true", help="Print the version number and exit"
    )

    args = parser.parse_args()
    if args.version:
        version()
        sys.exit(0)

    if args.outputfile:
        global output
        output = args.outputfile

    return args


# An abstraction of the getCollections and getPatients functions
# to generalize an interface for the CLI
def getResults_cli(func, **kwargs) -> None:
    """
    Executes the given function with the provided keyword arguments and prints the results.

    Args:
        func: The function to be executed.
        **kwargs: Keyword arguments to be passed to the function.

    Returns:
        None
    """

    global query
    global output
    # Execute the function
    results = cli_wrapper(func=func, **kwargs)

    # this is for the downloadSingleSeries function
    if results == True:
        return

    if not isinstance(results, list) or not len(results):
        return

    if output:
        writeResultsToFile(results, output)
        return

    if isinstance(results[0], dict):
        print("\t".join(results[0].keys()))
        for result in results:
            print("\t".join(str(value) for value in result.values()))  # type: ignore
    elif isinstance(results, list):
        for result in results:
            print(result)
    return


# create a helper function that will be used if the user ever uses --output <FILE>.tsv
# output should be a io.TextIOWrapper object
def writeResultsToFile(results: List, output: io.TextIOWrapper) -> None:
    """
    Writes the results of a query to a file.

    Args:
        results: The results of the query.
        output: The path to the output file.

    Returns:
        None
    """

    # write to the file
    if isinstance(results[0], dict):
        # write the header
        output.write("\t".join(results[0].keys()) + "\n")
        # write the results
        for result in results:
            output.write("\t".join(str(value) for value in result.values()) + "\n")
    else:
        # write the results
        for result in results:
            output.write(str(result) + "\n")
    return


def cli_wrapper(func, **kwargs) -> List[str] | None:
    """
    Wraps a function call with a loading animation.

    Args:
        func: The function to be called.
        **kwargs: Keyword arguments to be passed to the function.

    Returns:
        The result of the function call.

    """
    global done_event
    global query

    # # Start the loading animation in a separate thread
    # loading_thread = threading.Thread(target=loading_animation)

    # # daemon threads are killed when the main thread exits
    # loading_thread.daemon = True
    # loading_thread.start()

    # Perform the database query in the main thread
    result = func(**kwargs)

    # # Stop the loading animation
    # done_event.set()
    # loading_thread.join()

    return result


def getPatients_cli() -> None:
    global query
    query = "patients"
    p = _initialize_parser(description=f"NBIAToolkit: {query} ")

    p.add_argument(
        "-c",
        "--collection",
        action="store",
        required=True,
        type=str,
    )

    args = _add_extra_args(p)

    return getResults_cli(
        func=NBIAClient(args.username, args.password).getPatients,
        Collection=args.collection,
    )


def getCollections_cli() -> None:
    global query
    query = "collections"
    p = _initialize_parser(description=f"NBIAToolkit: {query} ")

    p.add_argument(
        "-p",
        "--prefix",
        action="store",
        default="",
        type=str,
        help="The prefix to filter collections by, i.e 'TCGA', 'LIDC', 'NSCLC'",
    )

    args = _add_extra_args(p)

    return getResults_cli(
        func=NBIAClient(args.username, args.password).getCollections, prefix=args.prefix
    )


def getNewPatients_cli() -> None:
    global query
    query = "newPatients"
    p = _initialize_parser(
        description=f"NBIAToolkit: {query}. Get new patients from a collection since a given date."
    )

    p.add_argument(
        "-c",
        "--collection",
        action="store",
        required=True,
        type=str,
    )

    p.add_argument(
        "-d",
        "--date",
        action="store",
        required=True,
        type=str,
        help="The date to filter by, i.e '2021-01-01' or '2019/12/31",
    )

    args = _add_extra_args(p)

    return getResults_cli(
        func=NBIAClient(args.username, args.password).getNewPatients,
        Collection=args.collection,
        Date=args.date,
    )


def getBodyPartCounts_cli() -> None:
    global query
    global output
    query = f"BodyPartCounts"

    p = _initialize_parser(description=f"NBIAToolkit: {query} ")

    p.add_argument(
        "-c",
        "--collection",
        dest="collection",
        action="store",
        default="",
        type=str,
    )

    args = _add_extra_args(p)

    return getResults_cli(
        func=NBIAClient(args.username, args.password).getBodyPartCounts,
        Collection=args.collection,
    )


def getStudies_cli() -> None:
    global query
    query = f"getStudies"
    p = _initialize_parser(
        description=f"NBIAToolkit: {query}. Get studies from a collection."
    )

    p.add_argument(
        "-c",
        "--collection",
        action="store",
        required=True,
        type=str,
    )

    p.add_argument(
        "-p",
        "--patientID",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "-s",
        "--studyInstanceUID",
        action="store",
        default="",
        type=str,
    )

    args = _add_extra_args(p)

    return getResults_cli(
        func=NBIAClient(args.username, args.password).getStudies,
        Collection=args.collection,
        PatientID=args.patientID,
        StudyInstanceUID=args.studyInstanceUID,
    )


def getSeries_cli() -> None:
    global query
    global output
    query = f"series"

    p = _initialize_parser(description=f"NBIAToolkit: {query} ")

    p.add_argument(
        "-c",
        "--collection",
        dest="collection",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "-p",
        "--patientID",
        dest="patientID",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "-m",
        "--modality",
        dest="modality",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "-study",
        "--studyInstanceUID",
        dest="studyInstanceUID",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "--seriesInstanceUID",
        dest="seriesInstanceUID",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "--bodyPartExamined",
        dest="bodyPartExamined",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "--manufacturerModelName",
        dest="manufacturerModelName",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "--manufacturer",
        dest="manufacturer",
        action="store",
        default="",
        type=str,
    )

    args = _add_extra_args(p)
    return getResults_cli(
        func=NBIAClient(args.username, args.password).getSeries,
        Collection=args.collection,
        PatientID=args.patientID,
        StudyInstanceUID=args.studyInstanceUID,
        Modality=args.modality,
        SeriesInstanceUID=args.seriesInstanceUID,
        BodyPartExamined=args.bodyPartExamined,
        ManufacturerModelName=args.manufacturerModelName,
        Manufacturer=args.manufacturer,
    )


def getNewSeries_cli() -> None:
    global query
    query = f"newSeries"
    p = _initialize_parser(
        description=f"NBIAToolkit: {query}. Get new series from a collection since a given date."
    )

    p.add_argument(
        "-d",
        "--date",
        action="store",
        required=True,
        type=str,
        help="The date to filter by, i.e '2021-01-01' or '2019/12/31",
    )

    args = _add_extra_args(p)

    return getResults_cli(
        func=NBIAClient(args.username, args.password).getNewSeries, Date=args.date
    )


def downloadSingleSeries_cli() -> None:
    global query
    query = f"series"
    # use the NBIAClient._downloadSingleSeries function to download a single series

    p = _initialize_parser(description="NBIAToolkit: download a single series")

    p.add_argument(
        "--seriesUID",
        dest="seriesUID",
        action="store",
        required=True,
        type=str,
    )

    p.add_argument(
        "--downloadDir",
        dest="downloadDir",
        action="store",
        required=True,
        type=str,
        help="The directory to download the series to",
    )

    p.add_argument(
        "--filePattern",
        dest="filePattern",
        action="store",
        type=str,
        default="%PatientID/%StudyInstanceUID/%SeriesInstanceUID/%SOPInstanceUID.dcm",
        help="The file pattern to use when downloading the series",
    )

    p.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing files",
    )

    args = p.parse_args()

    return getResults_cli(
        func=NBIAClient(args.username, args.password).downloadSeries,
        SeriesInstanceUID=args.seriesUID,
        downloadDir=args.downloadDir,
        filePattern=args.filePattern,
        overwrite=args.overwrite,
    )


# Create command line interface

# Given a source directory, destination directory, and target pattern, sort DICOM files
# into the destination directory according to the target pattern.
# The target pattern is a string with placeholders matching '%<DICOMKey>'.


def DICOMSorter_cli():
    parser = _initialize_parser(
        description="NBIAToolkit: Sort DICOM files into destination directory according to target pattern."
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
        help="Truncate the UID to the last 5 characters (includes periods & underscores). Default is True.",
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
        shutil_option="copy", overwrite=args.overwrite, n_parallel=int(args.nParallel)
    )
