
import io
from .nbia import NBIAClient, __version__


import argparse
import sys
import threading
from pyfiglet import Figlet
import sys
import subprocess

# import from typing libraries
from typing import List, Dict, Tuple, Union, Optional, Any

done_event = threading.Event()
query: str
output: io.TextIOWrapper | None = None


def version():
    f = Figlet(font="slant")
    print(f.renderText("NBIAToolkit"))
    print("Version: {}".format(__version__))

    # print all available command line tools:
    print("\nAvailable CLI tools: \n")

    # run each command with -h to see the available options
    commands = ["getCollections", "getPatients", "getBodyPartCounts", "getSeries", "downloadSingleSeries"]
    for command in commands:
        result = subprocess.run([command, "-h"], capture_output=True, text=True)
        output_lines = result.stdout.splitlines()
        # print out every line from the output until theres a line that contains "usage" in it
        for line in output_lines:
            if "NBIAToolkit" in line:
                break
            print(line[7:])

    return

def general_parser(parser: argparse.ArgumentParser) -> argparse.Namespace:
    parser.add_argument("-o", "--output", dest="outputfile",
        action="store", type=argparse.FileType('w', encoding='UTF-8'), help="Output file (tsv works best)",
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
    p = argparse.ArgumentParser(description=f"NBIAToolkit: {query} ")

    p.add_argument("-c", "--collection", action="store",
                   required=True,type=str,)

    args = general_parser(p)

    return getResults_cli(func=NBIAClient().getPatients, Collection=args.collection)


def getCollections_cli() -> None:
    global query
    query = "collections"
    p = argparse.ArgumentParser(description=f"NBIAToolkit: {query} ")

    p.add_argument("-p", "--prefix",
        action="store", default="", type=str,
        help="The prefix to filter collections by, i.e 'TCGA', 'LIDC', 'NSCLC'",
    )

    args = general_parser(p)

    return getResults_cli(func=NBIAClient().getCollections, prefix=args.prefix)


def getBodyPartCounts_cli() -> None:
    global query
    global output
    query = f"BodyPartCounts"

    p = argparse.ArgumentParser(description=f"NBIAToolkit: {query} ")

    p.add_argument("-c", "--collection", dest="collection",
        action="store", default="", type=str,)

    args = general_parser(p)


    return getResults_cli(func=NBIAClient().getBodyPartCounts, Collection=args.collection)


def getSeries_cli() -> None:
    global query
    global output
    query = f"series"

    p = argparse.ArgumentParser(description=f"NBIAToolkit: {query} ")

    p.add_argument("-c", "--collection", dest="collection", action="store",
        default="", type=str,
    )

    p.add_argument("-p", "--patientID", dest="patientID",
        action="store", default="", type=str,)

    p.add_argument("-m", "--modality", dest="modality",
        action="store", default="", type=str,)

    p.add_argument("-study", "--studyInstanceUID", dest="studyInstanceUID",
        action="store", default="", type=str,)


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

    args = general_parser(p)
    return getResults_cli(
        func=NBIAClient().getSeries,
        Collection=args.collection,
        PatientID=args.patientID,
        StudyInstanceUID=args.studyInstanceUID,
        Modality=args.modality,
        SeriesInstanceUID=args.seriesInstanceUID,
        BodyPartExamined=args.bodyPartExamined,
        ManufacturerModelName=args.manufacturerModelName,
        Manufacturer=args.manufacturer,
    )


def downloadSingleSeries_cli() -> None:
    global query
    query = f"series"
    # use the NBIAClient._downloadSingleSeries function to download a single series

    p = argparse.ArgumentParser(description="NBIAToolkit: download a single series")

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
        func=NBIAClient()._downloadSingleSeries,
        SeriesInstanceUID=args.seriesUID,
        downloadDir=args.downloadDir,
        filePattern=args.filePattern,
        overwrite=args.overwrite,
    )


