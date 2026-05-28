# UNIQLO China API reference

> Market: **uniqlo.cn** only (not uniqlo.com). Last reviewed: 2026-05-26.

## Scope

- Guest, read-only endpoints discovered from `https://www.uniqlo.cn` traffic
- Out of scope: login, cart mutation, checkout, payment, profile, address

## Base URLs

| Variable | Default | Role |
|----------|---------|------|
| `UNIQLO_API_BASE_URL` | `https://d.uniqlo.cn/p` | Hmall BFF services |
| `UNIQLO_WEB_BASE_URL` | `https://www.uniqlo.cn` | Static JSON under `/data/` |

## Endpoint catalog

| ID | Purpose | Method | Path (after base) |
|----|---------|--------|-------------------|
| `recommend-words` | Search suggestions | GET | `/hmall-bd-service/recommendWord/getRecommendWord/zh_CN` |
| `category-info` | Category metadata | POST | `/hmall-sc-service/search/searchCategoryInfo/zh_CN` |
| `product-listing` | PLP filters + products | POST | `/hmall-sc-service/search/searchWithCategoryCodeAndConditions/zh_CN` |
| `shop-classification` | PC nav tree | GET | `/data/shop_classification_PC.json` (web base) |
| `cms-config` | Site CMS config | GET | `/data/cms-config.json` (web base) |

## Stable fixtures

| Key | Value | Used by |
|-----|-------|---------|
| Category code | `3wtshirt` | Category info, product listing |
| Category page URL | `/c/3wtshirt.html` | Listing payload `url` field |
| Listing payload | `tests/api/payloads.py` → `TSHIRT_LISTING_PAYLOAD` | Live + docs |

## Hmall response envelope

```json
{
  "success": true,
  "total": 1,
  "resp": {}
}
```

- `assert_hmall_success` requires `success is True` and `resp` present
- When `total` is present and `resp` is a list, `total` must equal `len(resp)`

## Recorded offline fixtures

Under `tests/api/fixtures/` (validated by `offline_contract` tests):

| File | Endpoint family |
|------|-----------------|
| `recommend_words_success.json` | recommend-words |
| `category_info_3wtshirt_success.json` | category-info |
| `product_listing_3wtshirt_success.json` | product-listing |
| `shop_classification_pc.json` | shop-classification |
| `cms_config_sample.json` | cms-config (minimal shape) |

Refresh fixtures after intentional API shape changes:

```bash
python3 tests/api/scripts/validate_fixtures.py
python3 -m pytest tests/api -m offline_contract -q
```

## POST product listing body

See `TSHIRT_LISTING_PAYLOAD` in `tests/api/payloads.py` (copied from browser traffic for `3wtshirt`).

## Skip vs fail (live tests)

| Condition | Result |
|-----------|--------|
| DNS/TLS/timeout | `pytest.skip` |
| HTTP 403, 429, 5xx | `pytest.skip` |
| HTTP 404 on wrong path | **fail** (likely test bug) |
| HTTP 404 on fixture category id | refresh fixture data |
| Assertion on response body | **fail** |

## Changelog

- 2026-05-26: Added offline fixtures, CMS live test, `payloads.py`, reference split from SKILL.md
