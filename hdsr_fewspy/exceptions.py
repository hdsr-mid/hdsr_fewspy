class FewsWebServiceNotRunningError(Exception):
    pass


class StandAloneFewsWebServiceNotRunningError(Exception):
    pass


class UserNotFoundInHdsrFewspyAuthError(Exception):
    pass


class NoPermissionInHdsrFewspyAuthError(Exception):
    pass


class PiSettingsError(Exception):
    pass


class LocationIdsDoesNotExistErr(Exception):
    """get_multi_time_series: Some of the location ids do not exist."""

    pass


class ParameterIdsDoesNotExistErr(Exception):
    """get_multi_time_series: some of the parameters do not exists for the external parameter."""

    pass
