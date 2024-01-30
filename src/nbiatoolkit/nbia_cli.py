import glob
import re

from requests import patch
from .nbia import NBIAClient, __version__

import argparse
import os
import sys
import time, threading
from pprint import pprint
from pyfiglet import Figlet
import sys

# import from typing libraries
from typing import List, Dict, Tuple, Union, Optional, Any

done_event = threading.Event()
query: str
output: str | None = None


def version():
    f = Figlet(font="slant")
    print(f.renderText("NBIAToolkit"))
    print("Version: {}".format(__version__))
    return


# create a helper function that will be used if the user ever uses --output <FILE>.tsv
def writeResultsToFile(results: List, output: str) -> None:
    """
    Writes the results of a query to a file.

    Args:
        results: The results of the query.
        output: The path to the output file.

    Returns:
        None
    """

    # open the file in write mode
    with open(output, "w") as f:
        if isinstance(results[0], dict):
            # write the header
            f.write("\t".join(results[0].keys()) + "\n")
            # write the results
            for result in results:
                f.write("\t".join(str(value) for value in result.values()) + "\n")
        else:
            # write the results
            for result in results:
                f.write(str(result) + "\n")

    return


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
    if results == True:
        return

    # If the user specified an output file, write the results to the file
    if output and isinstance(results, list) and len(results):
        writeResultsToFile(results, output)
        return
    elif not isinstance(results, list) or not len(results):
        return
    # Print the result
    elif isinstance(results[0], dict) and len(results):
        print("\t".join(results[0].keys()))
        for result in results:
            print("\t".join(str(value) for value in result.values()))  # type: ignore
        return

    elif isinstance(results, list):
        for result in results:
            print(result)
        return

    print(f"No {query} found. Check parameters using -h or try again later.")
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

    # Start the loading animation in a separate thread
    loading_thread = threading.Thread(target=loading_animation)

    # daemon threads are killed when the main thread exits
    loading_thread.daemon = True
    loading_thread.start()

    # Perform the database query in the main thread
    result = func(**kwargs)

    # Stop the loading animation
    done_event.set()
    loading_thread.join()

    return result


def loading_animation():
    """
    Displays a loading animation while retrieving data.

    This function prints a loading animation to the console while data is being retrieved.
    It uses a list of animation strings and continuously prints them in a loop until the
    'done_event' is set. The animation strings are padded with spaces to the maximum length
    to ensure consistent display. The animation pauses for 0.5 seconds between each iteration.
    """
    global query

    animations = [
        "Retrieving " + query + "." * i + " This may take a few seconds"
        for i in range(4)
    ]

    # Find the maximum length of the loading animation strings
    # print(animations[0])
    while not done_event.is_set():
        if done_event.is_set():
            # clear the line
            # sys.stdout.write("\033[F")
            # print( len(animations[0]))
            # print(" " * len(animations[0]), end="\r")
            break


def getPatients_cli() -> None:
    global query
    global output
    query = "patients"
    p = general_argParser()

    p.add_argument(
        "--collection",
        dest="collection",
        action="store",
        required=True,
        type=str,
    )
    args = p.parse_args()

    if args.version:
        version()
        sys.exit(0)

    if args.output:
        output = args.output

    return getResults_cli(func=NBIAClient().getPatients, Collection=args.collection)


def getCollections_cli() -> None:
    global query
    global output
    query = "collections"

    p = general_argParser()

    p.add_argument(
        "--prefix",
        dest="prefix",
        action="store",
        default="",
        type=str,
        help="The prefix to filter collections by, i.e 'TCGA', 'LIDC', 'NSCLC'",
    )
    args = p.parse_args()
    if args.version:
        version()
        sys.exit(0)

    if args.output:
        output = args.output

    return getResults_cli(func=NBIAClient().getCollections, prefix=args.prefix)


def getBodyPartCounts_cli() -> None:
    p = argparse.ArgumentParser(description="NBIAToolkit: get body part counts")

    p.add_argument(
        "--collection",
        dest="collection",
        action="store",
        default="",
        type=str,
    )

    args = p.parse_args()

    global query
    query = f"BodyPartCounts"

    return getResults_cli(
        func=NBIAClient().getBodyPartCounts, Collection=args.collection
    )


def getSeries_cli() -> None:
    p = argparse.ArgumentParser(description="NBIAToolkit: get series")

    p.add_argument(
        "--collection",
        dest="collection",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "--patientID",
        dest="patientID",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "--studyInstanceUID",
        dest="studyInstanceUID",
        action="store",
        default="",
        type=str,
    )

    p.add_argument(
        "--modality",
        dest="modality",
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

    args = p.parse_args()

    global query
    query = f"series"

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


def general_argParser():
    global query
    p = argparse.ArgumentParser(description=f"NBIAToolkit: {query} ")

    p.add_argument(
        "--output",
        dest="output",
        action="store",
        type=str,
        help="Output file (tsv works best)",
    )

    p.add_argument(
        "--version", "-v", action="store_true", help="Print the version number and exit"
    )

    return p
