from fewspy.renier.collector import constants
from fewspy.renier.collector import RequestsRetrySession
from typing import Type

import hkvfewspy
import logging


logger = logging.getLogger(__name__)

PiRestType = Type[hkvfewspy.io.rest_fewspi.PiRest]  # noqa


def get_pi_rest_instance() -> PiRestType:
    pi = hkvfewspy.Pi(protocol=constants.PIWEBSERVICE_PROTOCOL)
    pi.setUrl(url=constants.PIWEBSERVICE_URL)
    query_parameters = pi.setQueryParameters(protocol=constants.PIWEBSERVICE_PROTOCOL)

    # test pi
    assert query_parameters.protocol == constants.PIWEBSERVICE_PROTOCOL
    assert query_parameters.query["omitMissing"] is False  # just a test.. I do not know what is affected by omitMissing

    # test response without hkvfewspy
    session = RequestsRetrySession()
    assert constants.PIWEBSERVICE_URL.endswith("/")
    get_filter_url = f"{constants.PIWEBSERVICE_URL}filters"
    response = session.get(url=get_filter_url)
    if response.status_code not in (200,):
        msg = (
            f"normal request (without hkvfewspy) for url {constants.PIWEBSERVICE_URL} resulted "
            f"in code={response.status_code} text={response.text}"
        )
        logger.error(msg)
        raise AssertionError(msg)
    return pi


def get_pi_soap_instance():
    # pi = hkvfewspy.Pi(protocol="soap")
    # pi.setClient(wsdl=constants.SOAP_PIWEBSERVICE_WSDL)
    msg = (
        "The SOAP service is deprecated and should not be used anymore. "
        "It is or will be removed in a future release of Delft-FEWS. "
        "See: Delft-FEWS End of Life Modules and Displays"
    )
    logger.error(msg)
    raise AssertionError(msg)
