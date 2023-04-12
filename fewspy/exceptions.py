class ErrorBase(Exception):
    def __init__(self, message, errors=None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        # Now for your custom code...
        self.errors = errors


class TsDownloadError(ErrorBase):
    pass


class TsReadError(ErrorBase):
    pass


class NoTsExistsError(ErrorBase):
    pass


class TsAnalyseError(ErrorBase):
    pass


class TsSaveResultsError(ErrorBase):
    pass


class FewsWebServiceNotRunningError(ErrorBase):
    pass


class StandAloneFewsWebServiceNotRunningError(ErrorBase):
    pass


class TsManagerGapError(ErrorBase):
    pass


class WisPeriodError(ErrorBase):
    pass


class CannotShiftWisPeriod(ErrorBase):
    pass


class IntLocHasMetaButNoDfClassifiedSubloc(ErrorBase):
    pass


class URLNotFoundError(ErrorBase):
    pass


class UserNotFoundInHdsrFewspyAuthError(ErrorBase):
    pass


class UserInvalidTokenHdsrFewspyAuthError(ErrorBase):
    pass


class NoPermissionInHdsrFewspyAuthError(ErrorBase):
    pass


class PiSettingsError(ErrorBase):
    pass
