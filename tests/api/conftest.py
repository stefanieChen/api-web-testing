from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import pytest
import requests
from requests import Response, Session

DEFAULT_UNIQLO_API_BASE_URL = "https://d.uniqlo.cn/p"
DEFAULT_UNIQLO_WEB_BASE_URL = "https://www.uniqlo.cn"


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Base URL for UNIQLO China service APIs discovered from site traffic."""
    return os.getenv("UNIQLO_API_BASE_URL", DEFAULT_UNIQLO_API_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def uniqlo_web_base_url() -> str:
    """Base URL for UNIQLO China public web JSON assets."""
    return os.getenv("UNIQLO_WEB_BASE_URL", DEFAULT_UNIQLO_WEB_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def api_client() -> Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json",
            "Referer": f"{DEFAULT_UNIQLO_WEB_BASE_URL}/",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 "
                "CursorSkillsPoC/1.0"
            ),
        }
    )
    yield session
    session.close()


@pytest.fixture
def request_or_skip() -> Callable[..., Response]:
    def _request_or_skip(session: Session, method: str, url: str, **kwargs: Any) -> Response:
        kwargs.setdefault("timeout", 10)
        try:
            response = session.request(method, url, **kwargs)
        except requests.RequestException as exc:
            pytest.skip(f"Live API is unavailable from this environment: {exc}")

        if response.status_code in {403, 429} or response.status_code >= 500:
            pytest.skip(f"Live API returned environmental status {response.status_code}")
        return response

    return _request_or_skip


@pytest.fixture
def assert_json_response() -> Callable[[Response, int], Any]:
    def _assert_json_response(response: Response, expected_status: int = 200) -> Any:
        assert response.status_code == expected_status, response.text
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type, f"Unexpected content type: {content_type}"
        return response.json()

    return _assert_json_response


@pytest.fixture
def assert_hmall_success() -> Callable[[dict[str, Any]], Any]:
    def _assert_hmall_success(payload: dict[str, Any]) -> Any:
        assert payload.get("success") is True, payload
        assert "resp" in payload, payload
        return payload["resp"]

    return _assert_hmall_success
