from datetime import datetime
from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.tests.fixtures import fixture_api_efcis_prod_point_biologie_no_download_dir


# silence flake8
fixture_api_efcis_prod_point_biologie_no_download_dir = fixture_api_efcis_prod_point_biologie_no_download_dir


def test_efcis_prod_locations_json(fixture_api_efcis_prod_point_biologie_no_download_dir):
    """
    <location locationId="20924">
    <shortName>20924 c02 Gemaal Goyerbrug</shortName>
    <lat>51.98814213752072</lat>
    <lon>5.243994665879352</lon>
    <x>145163.0</x>
    <y>444426.0</y>
    </location>
    """

    response = fixture_api_efcis_prod_point_biologie_no_download_dir.get_samples(
        location_id="20924",
        start_time=datetime(2020, 1, 1),
        end_time=datetime(2020, 1, 2),
        output_choice=OutputChoices.xml_response_in_memory,
    )
    assert response.status_code == 200
    assert (
        response.text
        == '<?xml version="1.0" encoding="UTF-8"?>\n<Samples xmlns="http://www.wldelft.nl/fews/PI" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.wldelft.nl/fews/PI https://fewsdocs.deltares.nl/schemas/version1.0/pi-schemas/pi_samples.xsd" version="1.25" xmlns:fs="http://www.wldelft.nl/fews/fs" xmlns:qualifierId="http://www.wldelft.nl/fews/qualifierId">\n    <timeZone>0.0</timeZone>\n</Samples>'  # noqa
    )
