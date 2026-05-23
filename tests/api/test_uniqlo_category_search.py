import pytest

pytestmark = pytest.mark.live_api


def test_tshirt_category_info_returns_expected_navigation_nodes(
    api_client,
    api_base_url,
    request_or_skip,
    assert_json_response,
    assert_hmall_success,
):
    response = request_or_skip(
        api_client,
        "POST",
        f"{api_base_url}/hmall-sc-service/search/searchCategoryInfo/zh_CN",
        json={"categoryCode": "3wtshirt"},
    )
    payload = assert_json_response(response)
    categories = assert_hmall_success(payload)

    assert isinstance(categories, list)
    assert categories, "Expected category metadata for 3wtshirt"
    assert {category["categoryCode"] for category in categories} >= {"3wtshirt"}

    tshirt_category = next(category for category in categories if category["categoryCode"] == "3wtshirt")
    assert tshirt_category["categoryName"] == "T恤"
    assert isinstance(tshirt_category["categorySequence"], int)


def test_tshirt_product_listing_returns_filter_metadata_and_products(
    api_client,
    api_base_url,
    request_or_skip,
    assert_json_response,
    assert_hmall_success,
):
    listing_payload = {
        "url": "/c/3wtshirt.html",
        "pageInfo": {"page": 1, "pageSize": 20, "withSideBar": "Y"},
        "belongTo": "pc",
        "rank": "overall",
        "priceRange": {"low": 0, "high": 0},
        "color": [],
        "size": [],
        "season": [],
        "material": [],
        "sex": [],
        "categoryFilter": {},
        "identity": [],
        "insiteDescription": "",
        "exist": [],
        "categoryCode": "3wtshirt",
        "searchFlag": False,
        "description": "",
    }

    response = request_or_skip(
        api_client,
        "POST",
        f"{api_base_url}/hmall-sc-service/search/searchWithCategoryCodeAndConditions/zh_CN",
        json=listing_payload,
    )
    payload = assert_json_response(response)
    response_sections = assert_hmall_success(payload)

    assert isinstance(response_sections, list)
    assert len(response_sections) >= 3

    filters, products, pagination = response_sections[:3]
    assert isinstance(filters, list)
    assert any(filter_group.get("name") == "尺码" for filter_group in filters)
    assert any(filter_group.get("name") == "颜色" for filter_group in filters)

    assert isinstance(products, list)
    assert products, "Expected at least one product in the T恤 category"
    assert isinstance(pagination, dict)
    assert pagination["productSum"] >= len(products)

    first_product = products[0]
    assert {"code", "name", "name4zhCN", "minPrice", "maxPrice", "stock"}.issubset(first_product)
    assert first_product["code"].isdigit()
    assert "T恤" in first_product["name4zhCN"]
    assert first_product["minPrice"] <= first_product["maxPrice"]
    assert first_product["stock"] in {"Y", "N"}
