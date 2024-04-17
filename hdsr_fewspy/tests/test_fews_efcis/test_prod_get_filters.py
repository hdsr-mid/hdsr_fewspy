from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.tests.test_fews_efcis.fixtures import fixture_api_efcis_production_point_fc_no_download_dir

import pytest


# silence flake8
fixture_api_efcis_production_point_fc_no_download_dir = fixture_api_efcis_production_point_fc_no_download_dir


def test_sa_filters_json(fixture_api_efcis_production_point_fc_no_download_dir):
    response = fixture_api_efcis_production_point_fc_no_download_dir.get_filters(output_choice=OutputChoices.json_response_in_memory)
    assert response.status_code == 200
