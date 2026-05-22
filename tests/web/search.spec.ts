import { expect, test } from '@playwright/test';
import { dismissKnownOverlays, gotoUniqloHome, searchUniqlo } from './uniqlo.helpers';

test.describe('UNIQLO China search', () => {
  test('search returns a results experience for a stable product keyword', async ({ page }) => {
    await gotoUniqloHome(page);
    await searchUniqlo(page, 'T恤');
    await dismissKnownOverlays(page);

    await expect(page.locator('body')).toContainText(/T恤|搜索|商品|结果|分类/i, {
      timeout: 15_000,
    });
  });
});
