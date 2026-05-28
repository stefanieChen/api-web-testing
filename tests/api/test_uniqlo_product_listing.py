import pytest

pytestmark = pytest.mark.live_api


def test_tshirt_product_listing_returns_filter_facets_and_product_cards(
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
    sections = assert_hmall_success(payload)

    assert isinstance(sections, list)
    assert len(sections) >= 3

    filters, products, pagination = sections[:3]
    assert isinstance(filters, list)
    assert any(filter_group.get("name") == "尺码" for filter_group in filters)
    assert any(filter_group.get("name") == "颜色" for filter_group in filters)

    assert isinstance(products, list)
    assert products, "Expected at least one product for 3wtshirt listing"
    assert isinstance(pagination, dict)
    assert pagination["productSum"] >= len(products)

    first_product = products[0]
    assert {"code", "name", "name4zhCN", "minPrice", "maxPrice", "stock"}.issubset(first_product)
    assert first_product["code"].isdigit()
    assert first_product["name"]
    assert "T恤" in first_product["name4zhCN"]
    assert isinstance(first_product["minPrice"], (int, float))
    assert isinstance(first_product["maxPrice"], (int, float))
    assert first_product["minPrice"] <= first_product["maxPrice"]
    assert first_product["stock"] in {"Y", "N"}
