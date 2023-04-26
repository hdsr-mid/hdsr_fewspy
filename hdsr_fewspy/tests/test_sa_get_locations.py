from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.tests.fixtures import fixture_api_sa_no_download_dir

import geopandas as gpd


# silence flake8
fixture_api_sa_no_download_dir = fixture_api_sa_no_download_dir


def test_sa_locations_json(fixture_api_sa_no_download_dir):
    response = fixture_api_sa_no_download_dir.get_locations(
        output_choice=OutputChoices.json_response_in_memory, show_attributes=True
    )
    assert response.status_code == 200
    data = response.json()
    assert sorted(data.keys()) == ["geoDatum", "locations", "version"]
    assert len(data["locations"]) == 5993
    found_first_location = data["locations"][0]
    assert sorted(found_first_location.keys()) == [
        "attributes",
        "description",
        "lat",
        "locationId",
        "lon",
        "shortName",
        "x",
        "y",
        "z",
    ]
    assert len(found_first_location["attributes"]) == 10
    assert found_first_location["attributes"][0] == {
        "name": "LOC_NAME",
        "type": "text",
        "id": "LOC_NAME",
        "value": "beg_062-LR_13_xruim",
    }
    assert found_first_location["attributes"][1] == {
        "name": "TYPE",
        "type": "text",
        "id": "TYPE",
        "value": "Puntmeting",
    }
    assert found_first_location["attributes"][2] == {
        "name": "LOC_ID",
        "type": "text",
        "id": "LOC_ID",
        "value": "beg_062",
    }

    response_no_attributes = fixture_api_sa_no_download_dir.get_locations(
        output_choice=OutputChoices.json_response_in_memory, show_attributes=False
    )
    found_first_location = response_no_attributes.json()["locations"][0]
    assert found_first_location["attributes"] == []


def test_sa_locations_pandas(fixture_api_sa_no_download_dir):
    expected_columns = [
        "attributes",
        "description",
        "geometry",
        "lat",
        "lon",
        "parent_location_id",
        "short_name",
        "x",
        "y",
        "z",
    ]

    # show_attributes=True
    gdf = fixture_api_sa_no_download_dir.get_locations(
        output_choice=OutputChoices.pandas_dataframe_in_memory, show_attributes=True
    )
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert sorted(gdf.columns) == expected_columns
    assert gdf.iloc[0].attributes[0] == {
        "name": "LOC_NAME",
        "type": "text",
        "id": "LOC_NAME",
        "value": "beg_062-LR_13_xruim",
    }
    assert gdf.iloc[0].attributes[1] == {"name": "TYPE", "type": "text", "id": "TYPE", "value": "Puntmeting"}

    # show_attributes=False
    gdf = fixture_api_sa_no_download_dir.get_locations(
        output_choice=OutputChoices.pandas_dataframe_in_memory, show_attributes=False
    )
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf.iloc[0].attributes == []
    assert gdf.iloc[1].attributes == []
