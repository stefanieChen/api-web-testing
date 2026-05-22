import re

import pytest

pytestmark = pytest.mark.live_api


def test_filter_users_by_username_returns_matching_profile(
    api_client,
    api_base_url,
    request_or_skip,
    assert_json_response,
):
    response = request_or_skip(api_client, "GET", f"{api_base_url}/users", params={"username": "Bret"})
    users = assert_json_response(response)

    assert isinstance(users, list)
    assert len(users) == 1

    user = users[0]
    assert user["username"] == "Bret"
    assert re.match(r"^[^@]+@[^@]+\.[^@]+$", user["email"])
    assert isinstance(user["address"], dict)
    assert {"street", "suite", "city", "zipcode", "geo"}.issubset(user["address"])


def test_list_posts_for_user_contains_only_requested_user(
    api_client,
    api_base_url,
    request_or_skip,
    assert_json_response,
):
    response = request_or_skip(api_client, "GET", f"{api_base_url}/posts", params={"userId": 1})
    posts = assert_json_response(response)

    assert isinstance(posts, list)
    assert posts, "Expected at least one post for user 1"
    assert all(post["userId"] == 1 for post in posts)
    assert all(isinstance(post["id"], int) for post in posts)
    assert all(isinstance(post["title"], str) and post["title"] for post in posts)
