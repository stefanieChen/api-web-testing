---
name: api-testing
description: >-
  Creates and runs Python API tests (pytest + requests) for read-only UNIQLO China
  storefront APIs on uniqlo.cn and d.uniqlo.cn. Use when editing tests/api, adding
  Hmall contract tests, or validating uniqlo.cn JSON endpoints. Not for uniqlo.com.
paths:
  - "tests/api/**/*.py"
  - "tests/api/fixtures/**/*.json"
  - "requirements.txt"
  - "pytest.ini"
---

# API Testing: UNIQLO China (uniqlo.cn)

Generate or update API tests aligned with this repository. Stack: **pytest + requests**. Target: read-only endpoints from `https://www.uniqlo.cn` so API and Web UI tests share the same product surface.

**Not in scope:** `uniqlo.com`, login, cart mutation, checkout, payment, profile, address.

For endpoint catalog, payloads, fixtures, and skip/fail rules, see [reference.md](reference.md).

Related UI flows: `.cursor/skills/web-ui-testing/SKILL.md`.

## Project contract

- Tests live in `tests/api/`; shared helpers in `tests/api/conftest.py`.
- Shared POST body for `3wtshirt` listing: `tests/api/payloads.py` → `TSHIRT_LISTING_PAYLOAD`.
- Name files `test_uniqlo_<resource_or_flow>.py`; tests `test_<behavior>_<expected_result>()`.
- Use `api_client`, `api_base_url`, `uniqlo_web_base_url` fixtures.
- Live calls: `request_or_skip(...)` (skips on network/403/429/5xx).
- Assertions: `assert_json_response(...)`, then `assert_hmall_success(...)` for Hmall APIs.
- Mark live network tests `@pytest.mark.live_api`.
- Mark fixture-only tests `@pytest.mark.offline_contract`.
- Keep tests independent.

## Commands

```bash
python3 -m pip install -r requirements.txt
python3 tests/api/scripts/validate_fixtures.py
python3 -m pytest tests/api -q
python3 -m pytest tests/api -m offline_contract -q
python3 -m pytest tests/api -m live_api -q
```

Environment overrides:

```bash
UNIQLO_API_BASE_URL=https://d.uniqlo.cn/p \
UNIQLO_WEB_BASE_URL=https://www.uniqlo.cn \
python3 -m pytest tests/api -q
```

## Assertion layers

1. **Transport** — status, JSON content-type (`assert_json_response`)
2. **Envelope** — `success`, `resp`, coherent `total` when list (`assert_hmall_success`)
3. **Shape** — required keys, nested structure
4. **Types** — e.g. digit `code`, numeric prices
5. **Semantics** — stable business rules (e.g. `3wtshirt` → `T恤`); avoid campaign-specific word lists

Prefer focused assertions. Do not snapshot full live responses.

## Offline vs live

| Marker | When |
|--------|------|
| `offline_contract` | Assert against `tests/api/fixtures/*.json`; always runs in CI |
| `live_api` | Hits public uniqlo.cn / d.uniqlo.cn; may skip if blocked |

When adding a new live endpoint, add a minimal redacted fixture and an `offline_contract` test.

## Minimal live example

```python
response = request_or_skip(
    api_client,
    "POST",
    f"{api_base_url}/hmall-sc-service/search/searchCategoryInfo/zh_CN",
    json={"categoryCode": "3wtshirt"},
)
payload = assert_json_response(response)
categories = assert_hmall_success(payload)
assert any(item["categoryCode"] == "3wtshirt" for item in categories)
```

Full patterns: [reference.md](reference.md) and existing tests in `tests/api/`.

## Agent checklist

1. Confirm endpoint in [reference.md](reference.md) or document it there.
2. Reuse `conftest.py` helpers and `payloads.py` when applicable.
3. Add live test (`live_api`) + offline fixture test (`offline_contract`) when shape is stable.
4. Run `validate_fixtures.py`, then `pytest tests/api -q`.
5. Report pass / skip / fail counts; distinguish environment skip from real failures.
6. Never commit secrets, cookies, or tokens.
