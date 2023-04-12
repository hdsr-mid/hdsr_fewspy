from fewspy.api_calls.base import GetRequest
from fewspy.constants.choices import OutputChoices
from fewspy.utils.conversions import attributes_to_array
from fewspy.utils.conversions import camel_to_snake_case
from fewspy.utils.conversions import geo_datum_to_crs
from fewspy.utils.conversions import xy_array_to_point
from typing import List

import geopandas as gpd
import logging


logger = logging.getLogger(__name__)


class GetLocations(GetRequest):
    """Get FEWS locations as a geopandas GeoDataFrame.

    Args:
        - attributes (list): if not emtpy, the location attributes to include as columns in the pandas DataFrame.
    Returns:
        gpd (geopandas.GeoDataFrame): GeoDataFrame with index "id" and columns "name" and "group_id".
    """

    url_post_fix = "locations"

    def __init__(self, attributes: List = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes = attributes

    @property
    def valid_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
            OutputChoices.pandas_dataframe_in_memory,
        ]

    def run(self):
        # do the request
        parameters = parameters_to_fews(parameters=locals(), pi_settings=self.pi_settings)
        response = self.retry_backoff_session.get(url=self.url, params=parameters, verify=self.pi_settings.ssl_verify)

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
            if self.attributes:
                gdf.loc[:, self.attributes] = attributes_to_array(
                    attribute_values=gdf["attributes"].values, attributes=self.attributes
                )
            gdf.drop(columns=["attributes"], inplace=True)

        else:
            logger.error(f"FEWS Server responds {response.text}")
            gdf = gpd.GeoDataFrame()

        return gdf
