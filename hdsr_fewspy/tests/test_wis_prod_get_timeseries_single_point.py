from datetime import datetime

import hdsr_fewspy
import pytest


def test_wis_prod_area():
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
        only_value_and_flag=True
    )
    assert sorted(df.columns) == ['flag', 'location_id', 'parameter_id', 'value']
    assert len(df) > 100

    # same request but then only_value_and_flag=False
    df2 = api.get_time_series_single(
        location_id="OW437001",
        parameter_id="H.G.0",
        start_time=datetime(year=2019, month=1, day=1),
        end_time=datetime(year=2019, month=1, day=2),
        drop_missing_values=True,
        output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory,
        only_value_and_flag=False
    )
    # deze assert klopt dus niet
    assert sorted(df2.columns) == ['date', 'flag', 'fs:PRIMAIR', 'fs:VISUEEL', 'location_id', 'parameter_id', 'time', 'value']
    assert len(df2) > 100



    # <series>
    # <header>
    # <type>instantaneous</type>
    # <moduleInstanceId>WerkFilter</moduleInstanceId>
    # <locationId>OW437001</locationId>
    # <parameterId>H.G.0</parameterId>
    # <timeStep unit="nonequidistant"/>
    # <startDate date="2019-01-01" time="00:00:00"/>
    # <endDate date="2019-02-01" time="00:00:00"/>
    # <missVal>-999.0</missVal>
    # <stationName>LANGE WEIDE_4370-w_Enkele Wiericke</stationName>
    # <lat>52.04179318897731</lat>
    # <lon>4.782705883990958</lon>
    # <x>113527.0</x>
    # <y>450558.0</y>
    # <z>-1.18</z>
    # <units>mNAP</units>
    # </header>
    # <event date="2019-01-01" time="00:00:00" value="-0.474" flag="0" fs:PRIMAIR="OK" fs:VISUEEL="OK"/>
    # <event date="2019-01-01" time="00:15:00" value="-0.474" flag="0" fs:PRIMAIR="OK" fs:VISUEEL="OK"/>
