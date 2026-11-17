import { expect, test } from '@playwright/test';
import path from 'node:path';

test('inicio con retrato fotografico, comparacion real y funciones actuales', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/');
  await expect(page.getByText('Humanizado en LUMIA', { exact: true })).toBeVisible();
  const images = page.locator('img[src^="/demo/"]');
  await expect(images).toHaveCount(6);
  await images.last().scrollIntoViewIfNeeded();
  await expect.poll(() => images.evaluateAll(nodes => nodes.every(n => (n as HTMLImageElement).complete && (n as HTMLImageElement).naturalWidth > 0))).toBe(true);
  await expect(page.locator('#herramientas article')).toHaveCount(9);
  await expect(page.getByRole('heading', { name: 'Restauración de fotos', exact: true })).toBeVisible();
  const slider = page.getByRole('slider', { name: 'Comparar antes y después' });
  await slider.focus();
  await slider.press('ArrowRight');
  await expect(slider).toHaveValue('51');
  await page.goto('/');
  await page.screenshot({ path: path.resolve('../docs/evidencias/mejoras_20261116/inicio_fotografico.png'), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(errors).toEqual([]);
});
