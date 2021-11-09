# SOAP protocol is deprecated! So you can only use REST
PIWEBSERVICE_PROTOCOL = "rest"
PIWEBSERVICE_URL = "http://webwis-prd01.ad.hdsr.nl:8081/OwdPiService/rest/fewspiservice/v1/"

# Test your request at:
# http://webwis-prd01.ad.hdsr.nl:8081/OwdPiService/test/fewspiservicerest/index.jsp

# Cannot find url?
# As a FEWS databeheerder:
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
