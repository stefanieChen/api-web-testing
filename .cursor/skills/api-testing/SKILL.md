---
name: api-testing
description: Use this skill when creating, reviewing, or running Python API tests with pytest and requests, especially files under tests/api or Python files named test_*.py. Follow the project fixtures, naming conventions, assertion style, and live API safety rules in this skill.
paths:
  - "tests/api/**/*.py"
  - "requirements.txt"
  - "pytest.ini"
---

# API Testing Skill: pytest + requests

Use this skill to generate or update API tests for this repository. The target stack is Python `pytest` + `requests`. Demo tests call JSONPlaceholder by default, but the same structure can be reused for other public or internal HTTP APIs.

## Project contract

- Put API tests in `tests/api/`.
- Keep shared fixtures and helpers in `tests/api/conftest.py`.
- Name test files `test_<resource_or_flow>.py`.
- Name tests `test_<behavior>_<expected_result>()`.
- Use `requests.Session` from the `api_client` fixture instead of creating ad hoc clients in each test.
- Read the API base URL from `api_base_url`; do not hard-code it in every test.
- Use `request_or_skip(...)` for live public API calls so temporary DNS, TLS, or service outages are reported as skipped demo tests rather than misleading product failures.
- Keep every test independent; do not rely on execution order or data created by another test.

## Commands

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest tests/api -q
```

Optional environment override:

```bash
JSONPLACEHOLDER_BASE_URL=https://jsonplaceholder.typicode.com python3 -m pytest tests/api -q
```

## Assertion pattern

Prefer a layered assertion style:

1. Transport: status code, content type, response availability.
2. Schema shape: JSON object/list, required keys, nested keys.
3. Type contracts: `id` is int, `email` is string, arrays contain objects.
4. Business semantics: filter result belongs to requested user, created resource echoes request payload.

Use direct assertions with meaningful messages. Avoid broad snapshot assertions against full live responses.

Good example:

```python
response = request_or_skip(api_client, "GET", f"{api_base_url}/posts/1")
payload = assert_json_response(response)

assert payload["id"] == 1
assert isinstance(payload["title"], str) and payload["title"]
assert {"userId", "id", "title", "body"}.issubset(payload)
```

Avoid:

```python
assert response.ok
assert response.json() == {"full": "large fixture copied from the internet"}
```

## Test data guidelines

- Keep payloads small and explicit in the test body unless reused by several tests.
- For JSONPlaceholder write-style demos, remember data is faked by the service and not persisted.
- Do not store secrets, tokens, cookies, or private endpoints in the repository.
- If adding authenticated APIs later, read credentials from environment variables and skip with a clear message when they are absent.

## Error handling for public APIs

Live public APIs can be temporarily unavailable from cloud runners. Tests should still assert real behavior when the service responds, but network failures should be skipped by `request_or_skip`.

Do not catch assertion failures. Only skip environmental failures such as connection timeout, DNS failure, TLS failure, or explicit block/rate-limit status if the helper supports that case.

## Generation checklist for Cursor Agent

When asked to add API tests:

1. Identify the resource and user-visible behavior to validate.
2. Reuse `api_client`, `api_base_url`, `request_or_skip`, and `assert_json_response` from `tests/api/conftest.py`.
3. Add focused tests under `tests/api/test_<resource>.py`.
4. Include positive assertions and at least one structural assertion.
5. Run `python3 -m pytest tests/api -q` and report pass/skip/fail counts.
6. If a live service is unavailable, keep the test code and document the skip reason.

## Complete reference example

```python
import pytest

pytestmark = pytest.mark.live_api


def test_get_post_by_id_returns_expected_contract(api_client, api_base_url, request_or_skip, assert_json_response):
    response = request_or_skip(api_client, "GET", f"{api_base_url}/posts/1")
    payload = assert_json_response(response)

    assert payload["id"] == 1
    assert isinstance(payload["userId"], int)
    assert isinstance(payload["title"], str) and payload["title"]
    assert isinstance(payload["body"], str) and payload["body"]
```
