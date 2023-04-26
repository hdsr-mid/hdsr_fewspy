class FewsWebServiceNotRunningError(Exception):
    pass


class StandAloneFewsWebServiceNotRunningError(Exception):
    pass


class UserNotFoundInHdsrFewspyAuthError(Exception):
    pass


class UserInvalidTokenHdsrFewspyAuthError(Exception):
    pass


class NoPermissionInHdsrFewspyAuthError(Exception):
    pass


class PiSettingsError(Exception):
    pass
