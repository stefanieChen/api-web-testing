---
name: api-testing
description: Use this skill when creating, reviewing, or running Python API tests with pytest and requests for UNIQLO China APIs discovered from www.uniqlo.cn network traffic, especially files under tests/api or Python files named test_*.py. Follow the project fixtures, naming conventions, assertion style, and live-site safety rules in this skill.
paths:
  - "tests/api/**/*.py"
  - "requirements.txt"
  - "pytest.ini"
---

# API Testing Skill: pytest + requests for UNIQLO China

Use this skill to generate or update API tests for this repository. The target stack is Python `pytest` + `requests`. API tests should exercise real, read-only UNIQLO China endpoints discovered from `https://www.uniqlo.cn` page traffic so API tests and Web UI tests validate the same product surface.

## Discovered API surface

Exploration with Playwright network capture found these stable, unauthenticated, read-only endpoints:

| Purpose | Method | Endpoint |
| --- | --- | --- |
| Search recommendation words | `GET` | `https://d.uniqlo.cn/p/hmall-bd-service/recommendWord/getRecommendWord/zh_CN` |
| Category metadata for `3wtshirt` | `POST` | `https://d.uniqlo.cn/p/hmall-sc-service/search/searchCategoryInfo/zh_CN` |
| Product listing for category filters | `POST` | `https://d.uniqlo.cn/p/hmall-sc-service/search/searchWithCategoryCodeAndConditions/zh_CN` |
| PC shop classification data | `GET` | `https://www.uniqlo.cn/data/shop_classification_PC.json` |
| CMS/page configuration data | `GET` | `https://www.uniqlo.cn/data/cms-config.json`, `https://www.uniqlo.cn/data/pages/<page>.json` |

Do not add tests for login, cart mutation, checkout, payment, user profile, or address APIs in this proof of concept.

## Project contract

- Put API tests in `tests/api/`.
- Keep shared fixtures and helpers in `tests/api/conftest.py`.
- Name test files `test_uniqlo_<resource_or_flow>.py`.
- Name tests `test_<behavior>_<expected_result>()`.
- Use `requests.Session` from the `api_client` fixture instead of creating ad hoc clients in each test.
- Read service API base URL from `api_base_url` (`UNIQLO_API_BASE_URL`, default `https://d.uniqlo.cn/p`).
- Read web JSON asset base URL from `uniqlo_web_base_url` (`UNIQLO_WEB_BASE_URL`, default `https://www.uniqlo.cn`).
- Use `request_or_skip(...)` for live public API calls so DNS, TLS, timeout, block, rate-limit, or server-side outages are reported as skipped demo tests rather than misleading product failures.
- Use `assert_json_response(...)` for transport/content-type/status assertions.
- Use `assert_hmall_success(...)` for Hmall service envelope assertions (`success: true`, `resp` exists).
- Keep every test independent; do not rely on execution order or data created by another test.

## Commands

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest tests/api -q
```

Optional environment overrides:

```bash
UNIQLO_API_BASE_URL=https://d.uniqlo.cn/p \
UNIQLO_WEB_BASE_URL=https://www.uniqlo.cn \
python3 -m pytest tests/api -q
```

## Request patterns

### GET Hmall service endpoint

```python
response = request_or_skip(
    api_client,
    "GET",
    f"{api_base_url}/hmall-bd-service/recommendWord/getRecommendWord/zh_CN",
)
payload = assert_json_response(response)
words = assert_hmall_success(payload)

assert isinstance(words, list)
assert payload["total"] == len(words)
assert {"wordId", "displaySequence", "wordName", "word", "id"}.issubset(words[0])
```

### POST category metadata endpoint

```python
response = request_or_skip(
    api_client,
    "POST",
    f"{api_base_url}/hmall-sc-service/search/searchCategoryInfo/zh_CN",
    json={"categoryCode": "3wtshirt"},
)
payload = assert_json_response(response)
categories = assert_hmall_success(payload)

assert any(category["categoryCode"] == "3wtshirt" for category in categories)
```

### POST product listing endpoint

```python
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

filters, products, pagination = sections[:3]
assert any(filter_group.get("name") == "尺码" for filter_group in filters)
assert products
assert pagination["productSum"] >= len(products)
```

## Assertion pattern

Prefer a layered assertion style:

1. Transport: status code, content type, response availability.
2. Service envelope: `success is True`, `resp` exists, `total` is coherent when present.
3. Schema shape: JSON object/list, required keys, nested keys.
4. Type contracts: product code is digit string, price is numeric, category sequence is int.
5. Business semantics: `3wtshirt` category is named `T恤`; T-shirt listings include product names containing `T恤`; top navigation includes `女装`, `男装`, `童装`, `婴幼儿装`.

Use direct assertions with meaningful messages. Avoid broad snapshot assertions against full live responses because campaign content and product order change frequently.

## Test data guidelines

- Prefer stable category code `3wtshirt` for product-listing demos.
- Prefer common Chinese product/search terms such as `T恤`, `衬衫`, `防晒衣`.
- Keep payloads small and copied from observed browser traffic.
- Do not store secrets, tokens, cookies, private endpoints, or user-specific identifiers in the repository.
- Do not write tests that mutate cart, order, favorite, address, login, payment, or profile state.
- If authenticated APIs are added later, read credentials from environment variables and skip with a clear message when they are absent.

## Error handling for public live APIs

UNIQLO China APIs can be temporarily unavailable or block cloud runners. Tests should still assert real behavior when the service responds, but network failures should be skipped by `request_or_skip`.

Do not catch assertion failures. Only skip environmental failures such as connection timeout, DNS failure, TLS failure, 403, 429, or 5xx responses.

## Generation checklist for Cursor Agent

When asked to add API tests:

1. Identify the UNIQLO endpoint from observed browser traffic or existing tests.
2. Reuse `api_client`, `api_base_url`, `uniqlo_web_base_url`, `request_or_skip`, `assert_json_response`, and `assert_hmall_success` from `tests/api/conftest.py`.
3. Add focused tests under `tests/api/test_uniqlo_<resource>.py`.
4. Include transport, envelope, structural, type, and user/business semantics assertions.
5. Keep tests read-only and unauthenticated.
6. Run `python3 -m pytest tests/api -q` and report pass/skip/fail counts.
7. If the live service is unavailable or blocks the runner, keep the test code and document the skip reason.
