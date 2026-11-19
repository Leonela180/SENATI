import { expect, test } from "@playwright/test";
import path from "node:path";

test("interfaz de escritorio y móvil: módulos, menú y ausencia de desbordamiento", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto("/registro");
  await page.getByLabel("Nombre").fill("Demo SENATI");
  await page.getByLabel("Correo").fill(`e2e+diseno${Date.now()}@demo.pe`);
  await page.getByLabel(/Contraseña/).fill("clave-segura-123");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page).toHaveURL(/\/app$/);
  await expect(page.getByRole("heading", { name: "Dale forma a tu próxima imagen." })).toBeVisible();
  await page.screenshot({ path: path.resolve("../docs/evidencias/mejoras_20261116/panel_escritorio.png"), fullPage: true });
  for (const route of ["estudio", "galeria", "generar", "horas", "equipo", "historial", "perfil", "humanizar"]) {
    await page.goto(`/app/${route}`);
    await expect(page.locator("h1")).toBeVisible();
    await expect(page.getByText("No pudimos cargar esta información")).toHaveCount(0);
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/app");
  await page.getByRole("button", { name: "Abrir menú" }).click();
  await page.getByRole("link", { name: "Equipo", exact: true }).click();
  await expect(page).toHaveURL(/\/app\/equipo$/);
  await expect(page.getByRole("button", { name: "Abrir menú" })).toBeVisible();
  for (const route of ["", "generar", "horas", "galeria", "estudio"]) {
    await page.goto(`/app/${route}`);
    await expect(page.locator("h1")).toBeVisible();
    expect(await page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")).toBe(true);
  }
  await page.goto("/app/generar");
  await page.screenshot({ path: path.resolve("../docs/evidencias/mejoras_20261116/gemini_movil.png"), fullPage: true });
  expect(errors).toEqual([]);
});
