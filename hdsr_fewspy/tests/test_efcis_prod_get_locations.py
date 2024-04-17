from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.tests.fixtures import fixture_api_efcis_prod_point_biologie_no_download_dir


# silence flake8
fixture_api_efcis_prod_point_biologie_no_download_dir = fixture_api_efcis_prod_point_biologie_no_download_dir


def test_efcis_prod_locations_json(fixture_api_efcis_prod_point_biologie_no_download_dir):
    response = fixture_api_efcis_prod_point_biologie_no_download_dir.get_locations(
        output_choice=OutputChoices.json_response_in_memory
    )
    assert response.status_code == 200
