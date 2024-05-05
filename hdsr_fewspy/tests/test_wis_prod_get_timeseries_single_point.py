from datetime import datetime

import hdsr_fewspy


def test_wis_prod_point():
    api = hdsr_fewspy.Api(
        pi_settings=hdsr_fewspy.DefaultPiSettingsChoices.wis_production_point_work,
    )
    df = api.get_time_series_single(
        location_id="OW437001",
        parameter_id="H.G.0",
        start_time=datetime(year=2019, month=1, day=1),
        end_time=datetime(year=2019, month=1, day=2),
        drop_missing_values=True,
        output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory,
        only_value_and_flag=True,
    )
    assert sorted(df.columns) == ["flag", "location_id", "parameter_id", "value"]
    assert len(df) > 100

    # same request but then only_value_and_flag=False
    df2 = api.get_time_series_single(
        location_id="OW437001",
        parameter_id="H.G.0",
        start_time=datetime(year=2019, month=1, day=1),
        end_time=datetime(year=2019, month=1, day=2),
        drop_missing_values=True,
        output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory,
        only_value_and_flag=False,
    )
    assert sorted(df2.columns) == [
        "date",
        "flag",
        "fs:PRIMAIR",
        "fs:VISUEEL",
        "location_id",
        "parameter_id",
        "time",
        "value",
    ]
    assert len(df2) > 100
