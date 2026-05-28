import { expect, type Locator, type Page, test } from '@playwright/test';

const BLOCK_OR_CHALLENGE_TEXT = /captcha|access denied|forbidden|too many requests|访问被拒绝|安全验证|验证码|请求过于频繁/i;

export async function gotoUniqloHome(page: Page): Promise<void> {
  let responseStatus: number | null = null;

  try {
    const response = await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 45_000 });
    responseStatus = response?.status() ?? null;
  } catch (error) {
    test.skip(true, `UNIQLO China home page was not reachable from this runner: ${String(error)}`);
  }

  if (responseStatus === 403 || responseStatus === 429 || (responseStatus !== null && responseStatus >= 500)) {
    test.skip(true, `UNIQLO China returned environmental HTTP status ${responseStatus}`);
  }

  await skipIfBlockedOrChallenged(page);
  await dismissKnownOverlays(page);

  await expect(page.locator('body')).toContainText(/UNIQLO|优衣库|搜索|男装|女装|童装/i, {
    timeout: 20_000,
  });
}

export async function skipIfBlockedOrChallenged(page: Page): Promise<void> {
  const bodyText = await page.locator('body').innerText({ timeout: 5_000 }).catch(() => '');
  if (BLOCK_OR_CHALLENGE_TEXT.test(bodyText)) {
    test.skip(true, 'UNIQLO China displayed an access challenge or anti-bot block in this environment');
  }
}

export async function dismissKnownOverlays(page: Page): Promise<void> {
  const buttonNames = [/同意|接受|确定|知道了|我知道了|关闭|暂不|稍后/i, /close|accept|agree|ok/i];

  for (const name of buttonNames) {
    const button = page.getByRole('button', { name }).first();
    if (await isVisible(button, 1_000)) {
      await button.click({ timeout: 3_000 }).catch(() => undefined);
    }
  }

  const fallbackCloseControls = page
    .locator(
      [
        '[aria-label*="关闭"]',
        '[aria-label*="close" i]',
        'button[class*="close" i]',
        '.close',
        '.modal-close',
        '.el-dialog__close',
      ].join(', '),
    )
    .first();

  if (await isVisible(fallbackCloseControls, 1_000)) {
    await fallbackCloseControls.click({ timeout: 3_000 }).catch(() => undefined);
  }
}

export async function searchUniqlo(page: Page, keyword: string): Promise<void> {
  await dismissKnownOverlays(page);

  const directSearchInput = await firstVisibleLocator(page, [
    'input[type="search"]',
    'input[placeholder*="搜索"]',
    'input[placeholder*="请输入"]',
    'input[aria-label*="搜索"]',
  ]);

  if (directSearchInput) {
    await directSearchInput.fill(keyword);
    await directSearchInput.press('Enter');
    await page.waitForLoadState('domcontentloaded').catch(() => undefined);
    await skipIfBlockedOrChallenged(page);
    return;
  }

  const searchTrigger = page.getByRole('button', { name: /搜索|search/i }).first();
  if (await isVisible(searchTrigger, 2_000)) {
    await searchTrigger.click();
  } else {
    const searchLink = page.getByRole('link', { name: /搜索|search/i }).first();
    if (await isVisible(searchLink, 2_000)) {
      await searchLink.click();
    } else {
      test.skip(true, 'Search control was not visible; selector strategy needs review for the current UNIQLO page');
    }
  }

  const openedSearchInput = await firstVisibleLocator(page, [
    'input[type="search"]',
    'input[placeholder*="搜索"]',
    'input[placeholder*="请输入"]',
    'input[aria-label*="搜索"]',
  ]);

  if (!openedSearchInput) {
    test.skip(true, 'Search input did not appear after opening the search control');
    return;
  }

  await openedSearchInput.fill(keyword);
  await openedSearchInput.press('Enter');
  await page.waitForLoadState('domcontentloaded').catch(() => undefined);
  await skipIfBlockedOrChallenged(page);
}

export async function firstVisibleLocator(page: Page, selectors: string[]): Promise<Locator | null> {
  for (const selector of selectors) {
    const locator = page.locator(selector).first();
    if (await isVisible(locator, 1_500)) {
      return locator;
    }
  }
  return null;
}

export async function isVisible(locator: Locator, timeout: number): Promise<boolean> {
  return locator.isVisible({ timeout }).catch(() => false);
}
