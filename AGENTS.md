# AGENTS.md

## Cursor Cloud specific instructions

This is a test-generation PoC with two stacks:

- **API tests** (Python): `python3 -m pytest tests/api -q`
- **Web UI tests** (Playwright/TypeScript): `npm run test:web`
- **Type check**: `npx tsc --noEmit`

### Non-obvious caveats

- `pip install` defaults to `--user` in this environment; pytest lands in `/home/ubuntu/.local/bin`. Ensure `PATH` includes that directory (the update script handles this via the `--break-system-packages` flag or user install).
- Playwright web tests target live external sites (`uniqlo.cn`, `jsonplaceholder.typicode.com`). Tests are designed to **skip gracefully** when the target is unreachable or rate-limited — this is expected, not a failure.
- `npm run test:web` uses headless Chromium only; the browser binary is cached under `~/.cache/ms-playwright/`.
- The `main` branch is essentially empty. Development work is on feature branches (e.g. `cursor/api-web-skills-poc-04c6`).

### Running services

No local services are required — all test targets are external public APIs/websites.
