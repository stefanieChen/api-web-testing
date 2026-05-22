from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import pytest
import requests
from requests import Response, Session

DEFAULT_BASE_URL = "https://jsonplaceholder.typicode.com"


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Base URL for JSONPlaceholder-compatible demo APIs."""
    return os.getenv("JSONPLACEHOLDER_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def api_client() -> Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "cursor-skills-api-tests/1.0",
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
