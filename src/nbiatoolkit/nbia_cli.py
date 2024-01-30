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

# import from typing libraries
from typing import List, Dict, Tuple, Union, Optional, Any

done_event = threading.Event()
query: str


def version():
    f = Figlet(font="slant")
    print(f.renderText("NBIAToolkit"))
    print("Version: {}".format(__version__))
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

    results = cli_wrapper(func=func, **kwargs)

    # Print the result
    if isinstance(results, list) and len(results):
        [print(patient) for patient in results]
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
    max_length = max(len(animation) for animation in animations)
    while not done_event.is_set():

        if done_event.is_set():
            # clear the line
            print(" " * max_length*2, end="\r", flush=True)
            break

        for animation in animations:
            # Pad the animation string with spaces to the maximum length
            padded_animation = animation.ljust(max_length).rstrip("\n")

            print(padded_animation, end="\r", flush=True)
            time.sleep(0.5)


def getPatients_cli() -> None:
    p = argparse.ArgumentParser(description="NBIAToolkit: get patient names")

    p.add_argument(
        "--collection", dest="collection", action="store", required=True, type=str,
    )

    args = p.parse_args()

    global query
    query = "patients"

    return getResults_cli(func=NBIAClient().getPatients, Collection=args.collection)


def getCollections_cli() -> None:
    p = argparse.ArgumentParser(description="NBIAtoolkit: get collection names")

    p.add_argument(
        "--prefix", dest="prefix", action="store", default="", type=str,
    )
    args = p.parse_args()

    global query
    query = "collections"

    return getResults_cli(func=NBIAClient().getCollections, prefix=args.prefix)



def getBodyPartCounts_cli() -> None:
    p = argparse.ArgumentParser(description="NBIAToolkit: get body part counts")

    p.add_argument(
        "--collection", dest="collection", action="store", default = "", type=str,
    )

    args = p.parse_args()

    global query
    query = f"BodyPartCounts"

    return getResults_cli(func=NBIAClient().getBodyPartCounts, Collection=args.collection)

