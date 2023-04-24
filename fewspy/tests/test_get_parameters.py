from fewspy.constants.choices import OutputChoices
from fewspy.tests.fixtures import fixture_api_sa_no_download_dir


# silence flake8
fixture_api_sa_no_download_dir = fixture_api_sa_no_download_dir


def test_sa_parameters_json(fixture_api_sa_no_download_dir):
    response = fixture_api_sa_no_download_dir.get_parameters(output_choice=OutputChoices.json_response_in_memory)
    assert response.status_code == 200


def test_sa_parameters_pandas_dataframe(fixture_api_sa_no_download_dir):
    df = fixture_api_sa_no_download_dir.get_parameters(output_choice=OutputChoices.pandas_dataframe_in_memory)
    assert len(df) == 272
    assert sorted(df.columns) == ["display_unit", "name", "parameter_group", "parameter_type", "unit", "uses_datum"]
