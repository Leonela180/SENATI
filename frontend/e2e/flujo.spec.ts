import { expect, test } from "@playwright/test";

test("registro → carga → humanización → comparación → descarga", async ({ page }) => {
  const email = `e2e+${Date.now()}@demo.pe`;
  await page.goto("/registro");
  await page.getByLabel("Nombre").fill("Prueba E2E");
  await page.getByLabel("Correo").fill(email);
  await page.getByLabel(/Contraseña/).fill("clave-segura-123");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page).toHaveURL(/\/app$/);

  await page.goto("/app/humanizar");
  await page.getByLabel("Seleccionar imagen").setInputFiles("e2e/fixtures/retrato_prueba.png");
  await page.getByLabel(/Confirmo que la imagen es generada por IA/).check();
  await page.getByRole("button", { name: "Humanizar imagen" }).click();
  await expect(page.getByRole("link", { name: "Descargar resultado" })).toBeVisible({ timeout: 240_000 });
  await expect(page.getByRole("slider", { name: "Comparar antes y después" })).toBeVisible();
  // Atajo: el resultado pasa al Estudio con «Textura de piel» ya elegida
  await page.getByRole("button", { name: "Agregar textura de piel" }).click();
  await expect(page).toHaveURL(/\/app\/estudio\?image=\d+&tool=textura_piel$/);
  await expect(page.getByRole("tab", { name: "Textura de piel" })).toHaveAttribute("aria-selected", "true");
});
