import pytest

pytestmark = pytest.mark.live_api


def test_get_post_by_id_returns_expected_contract(
    api_client,
    api_base_url,
    request_or_skip,
    assert_json_response,
):
    response = request_or_skip(api_client, "GET", f"{api_base_url}/posts/1")
    payload = assert_json_response(response)

    assert {"userId", "id", "title", "body"}.issubset(payload)
    assert payload["id"] == 1
    assert isinstance(payload["userId"], int)
    assert isinstance(payload["title"], str) and payload["title"]
    assert isinstance(payload["body"], str) and payload["body"]


def test_create_post_echoes_payload_and_returns_created(
    api_client,
    api_base_url,
    request_or_skip,
    assert_json_response,
):
    new_post = {
        "title": "cursor skill generated api test",
        "body": "This payload demonstrates pytest plus requests assertions.",
        "userId": 1,
    }

    response = request_or_skip(api_client, "POST", f"{api_base_url}/posts", json=new_post)
    payload = assert_json_response(response, expected_status=201)

    assert isinstance(payload["id"], int)
    assert payload["title"] == new_post["title"]
    assert payload["body"] == new_post["body"]
    assert payload["userId"] == new_post["userId"]
