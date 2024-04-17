from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.tests.test_fews_wis.fixtures import fixture_api_sa_work_no_download_dir


# silence flake8
fixture_api_sa_work_no_download_dir = fixture_api_sa_work_no_download_dir


def test_sa_qualifiers_json(fixture_api_sa_work_no_download_dir):
    response = fixture_api_sa_work_no_download_dir.get_qualifiers(output_choice=OutputChoices.xml_response_in_memory)
    assert response.status_code == 200

    # id      name               group_id
    # -----------------------------------
    # ergkrap erg krap (max 10%) None
    # krap    krap (max 30%)     None
    # normaal normaal (max 50%)  None
    # ruim    ruim (max 70%)     None
