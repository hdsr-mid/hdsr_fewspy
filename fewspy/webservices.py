from abc import ABC
from typing import List

import pandas as pd


class PiWebServiceSettingsBase(ABC):

    document_version: str = "1.25"
    protocol: str = "rest"  # SOAP protocol is deprecated! So you can only use REST
    missing_value: float = -999.0
    allowed_flags: List[int] = [0, 1, 2, 3, 4, 5]
    max_request_nr_timestamps: int = 100000  # parse_raw(xml=response.text) takes 4 sec with 96054 timestamps
    min_request_nr_timestamps: int = 10000
    max_request_period: pd.Timedelta = pd.Timedelta(weeks=52 * 2)

    @property
    def domain(self) -> str:
        raise NotImplementedError

    @property
    def port(self) -> int:
        raise NotImplementedError

    @property
    def base_url(self) -> str:
        raise NotImplementedError

    @property
    def test_url(self) -> str:
        raise NotImplementedError

    @property
    def filter_id(self) -> str:
        raise NotImplementedError

    @property
    def module_instance_id(self) -> str:
        raise NotImplementedError

    @property
    def default_request_period(self) -> pd.Timedelta:
        raise NotImplementedError

    @property
    def min_time_between_requests(self) -> pd.Timedelta:
        """Sleep if responseIf response time is was"""
        raise NotImplementedError

    @property
    def max_response_time(self) -> pd.Timedelta:
        """Warn if response time is above and adapt next request."""
        raise NotImplementedError

    @property
    def max_request_size_kb(self) -> int:
        """Warn if request size [kb] is above and adapt next request."""
        raise NotImplementedError


class StandAloneWebServiceSettings(PiWebServiceSettingsBase):
    @property
    def domain(self) -> str:
        return "localhost"

    @property
    def port(self) -> int:
        return 8081

    @property
    def base_url(self) -> str:
        return f"http://{self.domain}:{self.port}/FewsWebServices/rest/fewspiservice/v1/"

    @property
    def test_url(self) -> str:
        return f"http://{self.domain}:{self.port}/FewsWebServices/test/fewspiservicerest/index.jsp"

    @property
    def filter_id(self) -> str:
        # "RUW_OPVL": {"id": "RUW_OPVL", "name": "Oppervlaktewater (=alle mpt)"},
        # return "Oppervlaktewater"
        return "INTERAL-API.RUW_OPVL"

    @property
    def module_instance_id(self) -> str:
        # return "WerkFilter"
        # return "Ruwe metingen"
        # return "Webfilters Api"
        # return ""
        return "ImportOpvlWater"

    @property
    def default_request_period(self) -> pd.Timedelta:
        return pd.Timedelta(weeks=5)

    @property
    def min_time_between_requests(self) -> pd.Timedelta:
        return pd.Timedelta(seconds=1)

    @property
    def max_response_time(self) -> pd.Timedelta:
        return pd.Timedelta(seconds=20)

    @property
    def max_request_size_kb(self) -> int:
        return 3000


# Test your request at:
# http://webwis-prd01.ad.hdsr.nl:8081/OwdPiService/test/fewspiservicerest/index.jsp

# Cannot find url?
# As a FEWS databeheerder you find urls the following way:
# 1. open VDI
# 2. START (windows key)
# 3. unfold FEWS folder
# 4. Here are all the shortcuts to 3 PiWebServices (SWM, VIDENTE, OWD) both TEST and PRODUCTION (so 6 urls)
# NOTES:
# - OWD is most complete
#   - all oppervlaktewater, grondwater, neerslag (unfold Webfilters Api filter in WIS)
# - SWM is a subset (see kolom SWM in subloc.csv and ow_loc.csv)
#   - contains only NZK-ARK and NWW-MDV (unfold Webfilters Api filter in WIS)
# - VIDENTE is a subset (see ... ?)
#   - contains only waterstanden en debieten (unfold Webfilters Api filter in WIS)


class ProductionWebServiceSettings(PiWebServiceSettingsBase):
    @property
    def domain(self) -> str:
        return "webwis-prd01.ad.hdsr.nl"

    @property
    def port(self) -> int:
        return 8081

    @property
    def base_url(self) -> str:
        return f"http://{self.domain}:{self.port}/OwdPiService/rest/fewspiservice/v1/"

    @property
    def test_url(self) -> str:
        return f"http://{self.domain}:{self.port}/OwdPiService/test/fewspiservicerest/index.jsp"

    @property
    def filter_id(self) -> str:
        return "owdapi-opvlwater-noneq"

    @property
    def module_instance_id(self) -> str:
        # tijdseries tussen 8 mrt 2011 en 19 sep 2011 mogen we beschouwen als rommel (en dus niet naar
        # werkfilter gecopied) PI_OWD_API_STARTDATE = pd.Timestamp(year=2011, month=9, day=19)
        return "WerkFilter"

    @property
    def default_request_period(self) -> pd.Timedelta:
        return pd.Timedelta(weeks=26)

    @property
    def min_time_between_requests(self) -> pd.Timedelta:
        return pd.Timedelta(seconds=3)

    @property
    def max_response_time(self) -> pd.Timedelta:
        return pd.Timedelta(seconds=20)

    @property
    def max_request_size_kb(self) -> int:
        return 2000
