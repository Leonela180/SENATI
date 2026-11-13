import { expect, test, type Page } from "@playwright/test";

async function registrar(page: Page, nombre: string) {
  await page.goto("/registro");
  await page.getByLabel("Nombre").fill(nombre);
  await page.getByLabel("Correo").fill(`e2e+${nombre.toLowerCase()}${Date.now()}@demo.pe`);
  await page.getByLabel(/Contraseña/).fill("clave-segura-123");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page).toHaveURL(/\/app$/);
}

test("equipo: crear, invitar y unirse con el enlace (RF-18)", async ({ browser }) => {
  const dueno = await (await browser.newContext()).newPage();
  await registrar(dueno, "Duena");
  await dueno.goto("/app/equipo");
  await dueno.getByLabel("Nombre del equipo").fill("Equipo E2E");
  await dueno.getByRole("button", { name: "Crear equipo" }).click();
  await dueno.getByRole("button", { name: "Generar invitación" }).click();
  const enlace = await dueno.locator("input[readonly]").inputValue();
  expect(enlace).toContain("token=");

  const invitado = await (await browser.newContext()).newPage();
  await registrar(invitado, "Invitado");
  await invitado.goto(enlace);
  await expect(invitado.getByRole("heading", { name: "Equipo E2E" })).toBeVisible();
  await expect(invitado.getByText("Invitado", { exact: false }).first()).toBeVisible();
});
