from fewspy.constants.pi_settings import PiSettings
from fewspy.retry_session import RequestsRetrySession
from fewspy.utils.conversions import attributes_to_array
from fewspy.utils.conversions import camel_to_snake_case
from fewspy.utils.conversions import geo_datum_to_crs
from fewspy.utils.conversions import xy_array_to_point
from fewspy.utils.timer import Timer
from fewspy.utils.transformations import parameters_to_fews

import geopandas as gpd
import logging


logger = logging.getLogger(__name__)


def get_locations(
    url: str,
    #
    pi_setttings: PiSettings,
    retry_backoff_session: RequestsRetrySession,
    #
    attributes: list = None,
) -> gpd.GeoDataFrame:
    """Get FEWS locations as a geopandas GeoDataFrame.

    Args:
        - url (str): url Delft-FEWS PI REST WebService.
          e.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/qualifiers
        - attributes (list): if not emtpy, the location attributes to include as columns in the pandas DataFrame.
    Returns:
        gpd (geopandas.GeoDataFrame): GeoDataFrame with index "id" and columns "name" and "group_id".
    """
    # do the request
    timer = Timer()
    parameters = parameters_to_fews(parameters=locals(), pi_settings=pi_setttings)
    response = retry_backoff_session.get(url=url, parameters=parameters, verify=pi_setttings.ssl_verify)
    timer.report(message="Locations request")

    # parse the response
    if response.status_code == 200:
        # convert to gdf and snake_case
        gdf = gpd.GeoDataFrame(response.json()["locations"])
        gdf.columns = [camel_to_snake_case(i) for i in gdf.columns]
        gdf.set_index("location_id", inplace=True)

        # handle geometry and crs
        gdf["geometry"] = xy_array_to_point(xy_array=gdf[["x", "y"]].values)
        gdf.crs = geo_datum_to_crs(response.json()["geoDatum"])

        # handle attributes
        if attributes:
            gdf.loc[:, attributes] = attributes_to_array(
                attribute_values=gdf["attributes"].values, attributes=attributes
            )
        gdf.drop(columns=["attributes"], inplace=True)

        timer.report(message="Locations parsed")

    else:
        logger.error(f"FEWS Server responds {response.text}")
        gdf = gpd.GeoDataFrame()

    return gdf
