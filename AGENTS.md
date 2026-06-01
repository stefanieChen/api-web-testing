# AGENTS.md

## Cursor Cloud specific instructions

This is a test-generation PoC with two stacks:

- **API tests** (Python): `python3 -m pytest tests/api -q`
- **Web UI tests** (Playwright/TypeScript): `npm run test:web`
- **Type check**: `npx tsc --noEmit`

### Non-obvious caveats

- `pip install` defaults to `--user` in this environment; pytest lands in `/home/ubuntu/.local/bin`. Ensure `PATH` includes that directory (the update script handles this via the `--break-system-packages` flag or user install).
- API and Playwright web tests target live UNIQLO China endpoints/sites (`d.uniqlo.cn`, `www.uniqlo.cn`). Tests are designed to **skip gracefully** when the target is unreachable or rate-limited — this is expected, not a failure.
- `npm run test:web` uses headless Chromium only; the browser binary is cached under `~/.cache/ms-playwright/`.
- Prefer `python3 -m pytest` over bare `pytest` so tests run even when `/home/ubuntu/.local/bin` is not on `PATH`.

### Running services

No local services are required — all test targets are external public APIs/websites.
