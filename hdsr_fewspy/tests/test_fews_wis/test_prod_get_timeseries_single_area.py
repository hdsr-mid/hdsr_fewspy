from datetime import datetime

import hdsr_fewspy
import pytest


def test_prod_area_wrong():
    api = hdsr_fewspy.Api(
        pi_settings=hdsr_fewspy.DefaultPiSettingsChoices.wis_production_area_soilmoisture,
    )
    with pytest.raises(AssertionError) as err:
        api.get_time_series_single(
            location_id="AFVG13",
            parameter_id="SM.d",
            qualifier_id="does_not_exist",  # ["Lband05cm", "Lband10cm", "Lband20cm"]
            start_time=datetime(year=2015, month=1, day=1),
            end_time=datetime(year=2015, month=6, day=1),
            drop_missing_values=True,
            output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory,
        )
    assert err.value.args[0] == "qualifier_id 'does_not_exist' must be in ['Lband05cm', 'Lband10cm', 'Lband20cm']"


def test_prod_area():
    api = hdsr_fewspy.Api(
        pi_settings=hdsr_fewspy.DefaultPiSettingsChoices.wis_production_area_soilmoisture,
    )
    df = api.get_time_series_single(
        location_id="AFVG13",
        parameter_id="SM.d",
        qualifier_id="Lband05cm",  # ["Lband05cm", "Lband10cm", "Lband20cm"]
        start_time=datetime(year=2015, month=1, day=1),
        end_time=datetime(year=2015, month=6, day=1),
        drop_missing_values=True,
        output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory,
    )
    assert len(df) == 37
