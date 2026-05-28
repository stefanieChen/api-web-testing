import pytest

pytestmark = pytest.mark.offline_contract


def test_recommend_words_fixture_matches_hmall_contract(load_api_fixture, assert_hmall_success):
    payload = load_api_fixture("recommend_words_success.json")
    words = assert_hmall_success(payload)

    assert isinstance(words, list)
    first_word = words[0]
    assert {"wordId", "displaySequence", "wordName", "word", "id"}.issubset(first_word)
    assert first_word["wordName"] == first_word["word"]


def test_category_info_fixture_matches_hmall_contract(load_api_fixture, assert_hmall_success):
    payload = load_api_fixture("category_info_3wtshirt_success.json")
    categories = assert_hmall_success(payload)

    assert any(category["categoryCode"] == "3wtshirt" for category in categories)
    tshirt = next(category for category in categories if category["categoryCode"] == "3wtshirt")
    assert tshirt["categoryName"] == "T恤"


def test_product_listing_fixture_matches_hmall_contract(load_api_fixture, assert_hmall_success):
    payload = load_api_fixture("product_listing_3wtshirt_success.json")
    sections = assert_hmall_success(payload)

    filters, products, pagination = sections[:3]
    assert any(group.get("name") == "尺码" for group in filters)
    assert products[0]["code"].isdigit()
    assert pagination["productSum"] >= len(products)


def test_shop_classification_fixture_matches_expected_shape(load_api_fixture):
    payload = load_api_fixture("shop_classification_pc.json")
    classifications = payload["data"]

    top_level_titles = {item["title"] for item in classifications}
    assert {"女装", "男装", "童装", "婴幼儿装"}.issubset(top_level_titles)


def test_cms_config_fixture_is_non_empty_object(load_api_fixture):
    payload = load_api_fixture("cms_config_sample.json")
    assert isinstance(payload, dict)
    assert payload
