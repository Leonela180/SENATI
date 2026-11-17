import { expect, test } from "@playwright/test";

test("portada: herramientas actuales, vista previa y sin desbordes en celular", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("más reales");
  await expect(page.locator("#herramientas article")).toHaveCount(9);
  await expect(page.getByRole("heading", { name: "Restauración de fotos", exact: true })).toBeVisible();
  // Ejemplo real si existe /demo/demo.json; si no, capturas reales de la aplicación (nunca un antes/después simulado)
  const slider = page.getByRole("slider", { name: "Comparar antes y después" });
  const shots = page.locator('img[src^="/showcase/"]');
  await expect.poll(async () => (await slider.count()) + (await shots.count())).toBeGreaterThan(0);
  if (await slider.count()) {
    await slider.focus();
    await slider.press("ArrowRight");
    await expect(slider).toHaveValue("51");
  }
  await page.getByRole("link", { name: /Empezar gratis/ }).click();
  await expect(page).toHaveURL(/\/registro$/);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  expect(errors).toEqual([]);
});
