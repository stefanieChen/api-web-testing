import pytest

pytestmark = pytest.mark.live_api


def test_cms_config_returns_json_object(
    api_client,
    uniqlo_web_base_url,
    request_or_skip,
    assert_json_response,
):
    response = request_or_skip(
        api_client,
        "GET",
        f"{uniqlo_web_base_url}/data/cms-config.json",
    )
    payload = assert_json_response(response)

    assert isinstance(payload, dict)
    assert payload, "Expected non-empty CMS configuration JSON"

