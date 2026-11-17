import { expect, test } from "@playwright/test";

test("estudio: textura de piel muestra sus controles y avisa claro si no hay rostro", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/registro");
  await page.getByLabel("Nombre").fill("Piel Demo");
  await page.getByLabel("Correo").fill(`piel${Date.now()}@demo.pe`);
  await page.getByLabel(/Contraseña/).first().fill("clave-segura-123");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page).toHaveURL(/\/app$/);
  await page.goto("/app/estudio?tool=textura_piel");
  await page.getByLabel(/Confirmo que tengo permiso/).check();
  await page.locator('input[type="file"]').setInputFiles("e2e/fixtures/retrato_ilustrado.png");
  await expect(page.getByRole("tab", { name: "Textura de piel" })).toHaveAttribute("aria-selected", "true");
  await expect(page.getByText("Intensidad de la textura")).toBeVisible();
  await page.getByLabel("Agregar pecas suaves").check();
  await page.getByRole("button", { name: "Aplicar" }).click();
  // La ilustración de prueba no tiene un rostro detectable: el error debe ser claro, sin reintentos eternos
  await expect(page.getByRole("alert")).toContainText("No se encontró un rostro", { timeout: 30_000 });
  expect(errors).toEqual([]);
});
