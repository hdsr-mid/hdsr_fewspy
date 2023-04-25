from fewspy.api_calls.base import GetRequest
from fewspy.constants.choices import ApiParameters
from fewspy.constants.choices import OutputChoices
from fewspy.constants.custom_types import ResponseType
from fewspy.utils.conversions import camel_to_snake_case
from fewspy.utils.conversions import geo_datum_to_crs
from fewspy.utils.conversions import xy_array_to_point
from typing import List
from typing import Union

import geopandas as gpd
import logging
import pandas as pd


logger = logging.getLogger(__name__)


class GetLocations(GetRequest):
    def __init__(self, show_attributes: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_attributes = show_attributes

    @property
    def url_post_fix(self) -> str:
        return "locations"

    @property
    def allowed_request_args(self) -> List[str]:
        # possible args but we left out on purpose: paramterGroupId, includeLocationRelations, includeTimeDependency,
        return [
            ApiParameters.filter_id,
            ApiParameters.parameter_ids,
            ApiParameters.show_attributes,
            ApiParameters.document_format,
            ApiParameters.document_version,
        ]

    @property
    def required_request_args(self) -> List[str]:
        # fews sa almost crashes without a filter_id, so include it here
        return [ApiParameters.filter_id, ApiParameters.document_format, ApiParameters.document_version]

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
            OutputChoices.pandas_dataframe_in_memory,
        ]

    def run(self) -> Union[ResponseType, gpd.GeoDataFrame]:
        response = self.retry_backoff_session.get(
            url=self.url, params=self.filtered_fews_parameters, verify=self.pi_settings.ssl_verify
        )

        if self.output_choice in {OutputChoices.json_response_in_memory, OutputChoices.xml_response_in_memory}:
            return response

        assert self.output_choice == OutputChoices.pandas_dataframe_in_memory, "code error"
        # parse the response
        if response.status_code == 200:

            # convert to gdf and snake_case
            df = pd.json_normalize(data=response.json()["locations"])
            df.columns = [camel_to_snake_case(i) for i in df.columns]
            df.set_index("location_id", inplace=True)

            # handle geometry and crs
            gdf = gpd.GeoDataFrame(data=df)
            gdf["geometry"] = xy_array_to_point(xy_array=gdf[["x", "y"]].values)
            gdf.crs = geo_datum_to_crs(response.json()["geoDatum"])

        else:
            logger.error(f"FEWS Server responds {response.text}")
            gdf = gpd.GeoDataFrame()

        return gdf
