import pytest

pytestmark = pytest.mark.live_api


def test_recommend_words_returns_search_suggestions(
    api_client,
    api_base_url,
    request_or_skip,
    assert_json_response,
    assert_hmall_success,
):
    response = request_or_skip(
        api_client,
        "GET",
        f"{api_base_url}/hmall-bd-service/recommendWord/getRecommendWord/zh_CN",
    )
    payload = assert_json_response(response)
    words = assert_hmall_success(payload)

    assert isinstance(words, list)
    assert payload["total"] == len(words)
    assert words, "Expected UNIQLO search recommendation words"

    first_word = words[0]
    assert {"wordId", "displaySequence", "wordName", "word", "id"}.issubset(first_word)
    assert first_word["wordName"] == first_word["word"]
    assert first_word["displaySequence"].isdigit()
    assert any(word["wordName"] in {"衬衫", "短袖T恤", "防晒衣"} for word in words)


def test_shop_classification_contains_major_chinese_navigation_groups(
    api_client,
    uniqlo_web_base_url,
    request_or_skip,
    assert_json_response,
):
    response = request_or_skip(
        api_client,
        "GET",
        f"{uniqlo_web_base_url}/data/shop_classification_PC.json",
    )
    payload = assert_json_response(response)

    assert isinstance(payload, dict)
    classifications = payload["data"]
    assert isinstance(classifications, list)
    assert classifications, "Expected PC shop classification data"

    top_level_titles = {classification["title"] for classification in classifications}
    assert {"女装", "男装", "童装", "婴幼儿装"}.issubset(top_level_titles)

    women = next(classification for classification in classifications if classification["title"] == "女装")
    assert women["link"].startswith("/")
    assert isinstance(women["list"], list)

    child_titles = {
        child["title"]
        for group in women["list"]
        for child in group.get("childData", [])
        if "title" in child
    }
    assert "T恤" in child_titles
