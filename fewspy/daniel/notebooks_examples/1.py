def example():
    # https://github.com/d2hydro/fewspy/blob/main/notebooks/get_timeseries.ipynb

    from datetime import datetime
    from fewspy.api import Api

    import time

    LOCATION_IDS = [
        "NL34.HL.KGM154.LWZ1",
        "NL34.HL.KGM154.HWZ1",
        "NL34.HL.KGM154.KWK",
        "NL34.HL.KGM156.PMP2",
        "NL34.HL.KGM156.HWZ1",
        "NL34.HL.KGM155.HWZ1",
        "NL34.HL.KGM156.KSL1",
        "NL34.HL.KGM156.LWZ1",
        "NL34.HL.KGM156.PMP1",
        "NL34.HL.KGM154.PMP1",
        "NL34.HL.KGM155.LWZ1",
    ]
    PARAMETER_IDS = ["Q [m3/s] [NVT] [OW]", "WATHTE [m] [NAP] [OW]"]

    api = Api(url="https://www.hydrobase.nl/fews/nzv/FewsWebServices/rest/fewspiservice/v1/")

    time_series_set = api.get_time_series(
        filter_id="WDB_OW_KGM",
        location_ids=LOCATION_IDS,
        start_time=datetime(2022, 5, 1),
        end_time=datetime(2022, 5, 5),
        parameter_ids=PARAMETER_IDS,
    )

    time_series_set = api.get_time_series(
        filter_id="WDB_OW_KGM",
        location_ids=LOCATION_IDS,
        start_time=datetime(2022, 5, 1),
        end_time=datetime(2022, 5, 5),
        parameter_ids=PARAMETER_IDS,
        parallel=True,
    )
