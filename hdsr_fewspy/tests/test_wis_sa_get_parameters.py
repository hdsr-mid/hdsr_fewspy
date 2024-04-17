from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.tests.fixtures import fixture_api_wis_sa_work_no_download_dir


# silence flake8
fixture_api_wis_sa_work_no_download_dir = fixture_api_wis_sa_work_no_download_dir


def test_wis_sa_parameters_json(fixture_api_wis_sa_work_no_download_dir):
    response = fixture_api_wis_sa_work_no_download_dir.get_parameters(
        output_choice=OutputChoices.json_response_in_memory
    )
    assert response.status_code == 200


def test_wis_sa_parameters_xml(fixture_api_wis_sa_work_no_download_dir):
    output_choice = OutputChoices.xml_response_in_memory
    response = fixture_api_wis_sa_work_no_download_dir.get_parameters(output_choice=output_choice)
    assert response.status_code == 200


def test_wis_sa_parameters_pandas_dataframe(fixture_api_wis_sa_work_no_download_dir):
    df = fixture_api_wis_sa_work_no_download_dir.get_parameters(output_choice=OutputChoices.pandas_dataframe_in_memory)
    assert len(df) == 272
    assert sorted(df.columns) == ["display_unit", "name", "parameter_group", "parameter_type", "unit", "uses_datum"]
    expected_first_row = {
        "name": "Maaimoment",
        "parameter_type": "instantaneous",
        "unit": "-",
        "display_unit": "-",
        "uses_datum": False,
        "parameter_group": "TimeSteps",
    }
    assert df.iloc[0].to_dict() == expected_first_row
