from fewspy.constants import API_DOCUMENT_FORMAT
from fewspy.daniel.src.fewspy.utils.conversions import attributes_to_array
from fewspy.daniel.src.fewspy.utils.conversions import camel_to_snake_case
from fewspy.daniel.src.fewspy.utils.conversions import geo_datum_to_crs
from fewspy.daniel.src.fewspy.utils.conversions import xy_array_to_point
from fewspy.daniel.src.fewspy.utils.timer import Timer
from fewspy.daniel.src.fewspy.utils.transformations import parameters_to_fews

import geopandas as gpd
import logging
import pandas as pd
import requests


logger = logging.getLogger(__name__)


def get_locations(
    url: str,
    filter_id: str = None,
    document_format: str = API_DOCUMENT_FORMAT,
    attributes: list = [],
    verify: bool = False,
) -> pd.DataFrame:
    """Get FEWS qualifiers as a pandas DataFrame.
    Args:
        - url (str): url Delft-FEWS PI REST WebService.
          e.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/qualifiers
        - filter_id (str): the FEWS id of the filter to pass as request parameter
        - document_format (str): request document format to return. Defaults to PI_JSON.
        - attributes (list): if not emtpy, the location attributes to include as columns in the pandas DataFrame.
        - verify (bool, optional): passed to requests.get verify parameter. Defaults to False.
    Returns:
        df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
    """
    # do the request
    timer = Timer(logger)
    parameters = parameters_to_fews(parameters=locals())
    response = requests.get(url, parameters, verify=verify)
    timer.report(message="Locations request")

    # parse the response
    if response.status_code == 200:
        # convert to gdf and snake_case
        gdf = gpd.GeoDataFrame(response.json()["locations"])
        gdf.columns = [camel_to_snake_case(i) for i in gdf.columns]
        gdf.set_index("location_id", inplace=True)

        # handle geometry and crs
        gdf["geometry"] = xy_array_to_point(gdf[["x", "y"]].values)
        gdf.crs = geo_datum_to_crs(response.json()["geoDatum"])

        # handle attributes
        if attributes:
            gdf.loc[:, attributes] = attributes_to_array(gdf["attributes"].values, attributes)
        gdf.drop(columns=["attributes"], inplace=True)

        timer.report(message="Locations parsed")

    else:
        logger.error(f"FEWS Server responds {response.text}")
        gdf = gpd.GeoDataFrame()

    return gdf
