import requests
import responses


@responses.activate
def test_mock_google_response_works():
    # mock response
    url = "https://www.google.nl/"
    response_json = {"error": "not found"}
    status_code = 404
    responses.add(method=responses.GET, url=url, json=response_json, status=status_code)

    # check response
    resp = requests.get(url=url)
    assert resp.status_code == status_code
    assert resp.json() == response_json
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
