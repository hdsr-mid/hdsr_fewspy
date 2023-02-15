from gapfinder.constants.webservices import StandAloneWebServiceSettings
from gapfinder.hdsr_hkvfewspy.pi_rest import TimeSeriesCols
from gapfinder.tests.fixtures import get_df_wis_ts
from gapfinder.tests.fixtures import ts_analyser_fixture


# silence flake8
ts_analyser_fixture = ts_analyser_fixture


def test_flags_ignored(ts_analyser_fixture):
    pi_rest_settings = StandAloneWebServiceSettings()
    df_test_input = get_df_wis_ts()
    input_flags = df_test_input[TimeSeriesCols.flag].to_list()
    assert max(input_flags) > max(pi_rest_settings.allowed_flags)

    nr_rows_filtered_flags_and_value = len(
        df_test_input[
            (df_test_input[TimeSeriesCols.flag].isin(pi_rest_settings.allowed_flags))
            & (df_test_input[TimeSeriesCols.value] != pi_rest_settings.missing_value)
        ]
    )
    assert len(ts_analyser_fixture.orig_df_ts) == len(df_test_input)
    # in normal_gap_analyser we filter both on flags and missing_values
    assert len(ts_analyser_fixture.normal_gap_analyser.df_ts) == nr_rows_filtered_flags_and_value
    # in quarter_gap_analyser we filter both on flags and missing_values, we floor ts to whole minutes and then keep
    # 1 ts per quarter (+- 1 minute)
    assert len(ts_analyser_fixture.quarter_gap_analyser.df_ts) == 13
