from gapfinder.tests._expected_df_filters import expected_owd_filters_prd
from gapfinder.tests.fixtures import loc_date_query_parameters_kw100111_f0
from gapfinder.tests.fixtures import loc_date_query_parameters_ow100102_hg0
from gapfinder.tests.fixtures import production_pi_rest

import pandas as pd


# silence flake8
loc_date_query_parameters_kw100111_f0 = loc_date_query_parameters_kw100111_f0
loc_date_query_parameters_ow100102_hg0 = loc_date_query_parameters_ow100102_hg0
production_pi_rest = production_pi_rest

_index1 = pd.Timestamp("2012-10-28 00:00:00+0000", tz="Etc/GMT-0")
_index2 = pd.Timestamp("2012-10-28 00:15:00+0000", tz="Etc/GMT-0")

df_expected_first_two_rows = pd.DataFrame(
    data={
        "moduleInstanceId": {_index1: "WerkFilter", _index2: "WerkFilter"},
        "qualifierId": {_index1: "", _index2: ""},
        "parameterId": {_index1: "F.0", _index2: "F.0"},
        "units": {_index1: "Hz", _index2: "Hz"},
        "locationId": {_index1: "KW100111", _index2: "KW100111"},
        "stationName": {
            _index1: "WIJKERSLOOT_1001-K_WIJKERSLOOT-pompvijzel1_aanvoer",
            _index2: "WIJKERSLOOT_1001-K_WIJKERSLOOT-pompvijzel1_aanvoer",
        },
        "flag": {_index1: 0, _index2: 0},
        "value": {_index1: 0.0, _index2: 0.0},
    },
)


def test_prd_filters(production_pi_rest):
    """getFilters() return all filters regardless of module_instance_id and filter_id."""
    expected_base_url = "http://webwis-prd01.ad.hdsr.nl:8081/OwdPiService/rest/fewspiservice/v1/"
    assert production_pi_rest.settings.base_url == expected_base_url
    assert production_pi_rest.settings.module_instance_id == "WerkFilter"
    assert production_pi_rest.settings.filter_id == "owdapi-opvlwater-noneq"
    df_filters = production_pi_rest.hkv_pi.getFilters()
    pd.testing.assert_frame_equal(left=df_filters, right=expected_owd_filters_prd)
