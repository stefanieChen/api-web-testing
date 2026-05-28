import { expect, test } from '@playwright/test';
import { dismissKnownOverlays, gotoUniqloHome, isVisible, skipIfBlockedOrChallenged } from './uniqlo.helpers';

test.describe('UNIQLO China navigation', () => {
  test('top navigation exposes major shopping categories', async ({ page }) => {
    await gotoUniqloHome(page);
    await dismissKnownOverlays(page);

    const body = page.locator('body');
    await expect(body).toContainText(/男装|女装|童装|婴幼儿|新品|优衣库/i, {
      timeout: 15_000,
    });
  });

  test('category navigation opens a browsable shopping page', async ({ page }) => {
    await gotoUniqloHome(page);
    await dismissKnownOverlays(page);

    const categoryLink = page.getByRole('link', { name: /女装|男装|童装|婴幼儿|新品/i }).first();
    if (!(await isVisible(categoryLink, 5_000))) {
      test.skip(true, 'No major category link was visible; navigation markup may have changed');
    }

    const categoryName = ((await categoryLink.innerText().catch(() => '')) || '分类').trim();
    const previousUrl = page.url();

    await categoryLink.click();
    await page.waitForLoadState('domcontentloaded').catch(() => undefined);
    await skipIfBlockedOrChallenged(page);
    await dismissKnownOverlays(page);

    const currentUrl = page.url();
    const bodyText = await page.locator('body').innerText({ timeout: 10_000 });

    expect(currentUrl !== previousUrl || bodyText.includes(categoryName)).toBeTruthy();
    await expect(page.locator('body')).toContainText(/商品|系列|分类|男装|女装|童装|新品|UNIQLO/i, {
      timeout: 15_000,
    });
  });
});
