---
name: web-ui-testing
description: Use this skill when creating, reviewing, or running Playwright TypeScript Web UI tests for https://www.uniqlo.cn, especially tests under tests/web. Follow the locator strategy, Chinese e-commerce handling, popup handling, anti-bot resilience, and execution commands in this skill.
paths:
  - "tests/web/**/*.ts"
  - "playwright.config.ts"
  - "package.json"
---

# Web UI Testing Skill: Playwright + TypeScript for UNIQLO China

Use this skill to generate or update Playwright Web E2E tests for the UNIQLO China website (`https://www.uniqlo.cn`). The tests are live-site demonstrations, so they must be resilient to content changes, regional popups, slow network, and occasional bot/rate-limit defenses.

## Project contract

- Put Web UI specs in `tests/web/`.
- Name files `<flow>.spec.ts`, for example `search.spec.ts` or `navigation.spec.ts`.
- Put shared helpers in `tests/web/uniqlo.helpers.ts`.
- Use the base URL from `playwright.config.ts`; do not repeat `https://www.uniqlo.cn` in every test.
- Use TypeScript and Playwright Test (`@playwright/test`).
- Prefer user-observable flows over DOM implementation details.
- Keep tests independent and avoid relying on a logged-in account.

## Commands

```bash
npm install
npx playwright install chromium
npm run test:web
```

For local debugging:

```bash
npm run test:web:headed
npx playwright test tests/web/search.spec.ts --debug
```

Optional environment override:

```bash
UNIQLO_BASE_URL=https://www.uniqlo.cn npm run test:web
```

## Locator strategy

Use selectors in this order:

1. `getByRole` with accessible names visible to users, including Chinese labels such as `搜索`, `男装`, `女装`, `童装`.
2. `getByPlaceholder` for search fields such as `搜索`, `请输入`, `search`.
3. Stable attributes if present, such as `data-testid`, `data-qa`, or semantic `aria-*` attributes.
4. CSS selectors only as a fallback for common controls such as close buttons or search inputs.

Avoid brittle selectors based on generated classes, exact DOM depth, or large text blocks that change during campaigns.

## Chinese e-commerce site handling

When testing `www.uniqlo.cn`:

- Set `locale: 'zh-CN'` and `timezoneId: 'Asia/Shanghai'` in Playwright config.
- Use a desktop viewport; many e-commerce layouts hide navigation differently on mobile.
- Expect promotional popups, cookie prompts, region prompts, floating ads, and mini-program banners.
- Call `dismissKnownOverlays(page)` after navigation and before interacting with navigation or search.
- Use product keywords that are stable and common, for example `T恤`, `衬衫`, `羽绒服`.
- Assert on durable outcomes: URL changed, body contains the searched keyword, body contains category text, or the page exposes product/search result wording.
- Do not automate checkout, login, account creation, or payment flows in this proof of concept.

## Anti-bot and live-site resilience

Live public websites may block cloud IPs, show CAPTCHA, return 403/429, or time out. The demo helpers should skip environmental blocks with a clear reason, while still failing on real assertion mismatches after the page loads.

Acceptable skip reasons:

- Navigation timeout before the home page is usable.
- HTTP 403, 429, or 5xx on the initial page load.
- CAPTCHA / access denied / forbidden content detected in the page body.
- A site redesign removes the searched control entirely; skip with a message that the selector strategy needs review.

Do not hide test failures caused by assertions after a valid page interaction.

## Test structure pattern

```ts
import { expect, test } from '@playwright/test';
import { dismissKnownOverlays, gotoUniqloHome, searchUniqlo } from './uniqlo.helpers';

test('search returns a results experience for a stable product keyword', async ({ page }) => {
  await gotoUniqloHome(page);
  await searchUniqlo(page, 'T恤');
  await dismissKnownOverlays(page);

  await expect(page.locator('body')).toContainText(/T恤|搜索|商品|结果/, {
    timeout: 15_000,
  });
});
```

## Generation checklist for Cursor Agent

When asked to add Web UI tests:

1. Identify the user flow: search, top navigation, category browsing, product listing, or store information.
2. Reuse `gotoUniqloHome`, `dismissKnownOverlays`, `searchUniqlo`, and `skipIfBlockedOrChallenged` from `tests/web/uniqlo.helpers.ts`.
3. Prefer accessible locators and Chinese user-facing labels.
4. Add robust assertions on user-observable outcomes.
5. Keep waits event-based (`toBeVisible`, `toContainText`, `waitForLoadState`) instead of fixed sleeps.
6. Run `npm run test:web` and report pass/skip/fail counts.
7. If the live site blocks the runner, keep the test code and document the environmental skip reason.
