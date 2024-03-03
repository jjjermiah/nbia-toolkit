from typing import Any, List
from .nbia_endpoints import ReturnType
import pandas as pd


# function that takes a list of dictionaries and returns either a list or a dataframe
def conv_response_list(
    response_json: List[dict[Any, Any]],
    return_type: ReturnType,
) -> List[dict[Any, Any]] | pd.DataFrame:
    """Function that takes in a list of dictionaries and returns either a list or a dataframe.

    :param response_json: A response from the API in the form of a list of dictionaries.
    :type response_json: List[dict[Any, Any]]
    :param return_type: The desired return type for the response.
    :type return_type: ReturnType
    :return: Either a list of dictionaries or a DataFrame.
    :rtype: List[dict[Any, Any]] | pd.DataFrame
    """

    assert isinstance(response_json, list), "The response JSON must be a list"

    if return_type == ReturnType.LIST:
        return response_json
    elif return_type == ReturnType.DATAFRAME:
        return pd.DataFrame(data=response_json)
