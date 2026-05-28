from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import requests
from requests import Response, Session

DEFAULT_UNIQLO_API_BASE_URL = "https://d.uniqlo.cn/p"
DEFAULT_UNIQLO_WEB_BASE_URL = "https://www.uniqlo.cn"
API_FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Base URL for UNIQLO China service APIs discovered from site traffic."""
    return os.getenv("UNIQLO_API_BASE_URL", DEFAULT_UNIQLO_API_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def uniqlo_web_base_url() -> str:
    """Base URL for UNIQLO China public web JSON assets."""
    return os.getenv("UNIQLO_WEB_BASE_URL", DEFAULT_UNIQLO_WEB_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def api_client(uniqlo_web_base_url: str) -> Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json",
            "Referer": f"{uniqlo_web_base_url}/",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 "
                "CursorSkillsPoC/1.0"
            ),
        }
    )
    yield session
    session.close()


def request_or_skip(session: Session, method: str, url: str, **kwargs: Any) -> Response:
    """Call a live public API; skip the test on environmental failures."""
    kwargs.setdefault("timeout", 10)
    try:
        response = session.request(method, url, **kwargs)
    except requests.RequestException as exc:
        pytest.skip(f"Live API is unavailable from this environment: {exc}")

    if response.status_code in {403, 429} or response.status_code >= 500:
        pytest.skip(f"Live API returned environmental status {response.status_code}")
    return response


def assert_json_response(response: Response, expected_status: int = 200) -> Any:
    assert response.status_code == expected_status, response.text
    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type, f"Unexpected content type: {content_type}"
    return response.json()


def assert_hmall_success(payload: dict[str, Any]) -> Any:
    assert payload.get("success") is True, payload
    assert "resp" in payload, payload
    resp = payload["resp"]
    if "total" in payload and isinstance(resp, list):
        assert payload["total"] == len(resp), payload
    return resp


def load_api_fixture(name: str) -> Any:
    path = API_FIXTURES_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Missing API fixture: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(name="request_or_skip")
def request_or_skip_fixture() -> Callable[..., Response]:
    return request_or_skip


@pytest.fixture(name="assert_json_response")
def assert_json_response_fixture() -> Callable[[Response, int], Any]:
    return assert_json_response


@pytest.fixture(name="assert_hmall_success")
def assert_hmall_success_fixture() -> Callable[[dict[str, Any]], Any]:
    return assert_hmall_success


@pytest.fixture(name="load_api_fixture")
def load_api_fixture_fn() -> Callable[[str], Any]:
    return load_api_fixture
