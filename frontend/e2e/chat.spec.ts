import { expect, test } from "@playwright/test";

test("chat asistente: responde con la guía local sin clave y lleva a la herramienta", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/registro");
  await page.getByLabel("Nombre").fill("Chat Demo");
  await page.getByLabel("Correo").fill(`chat${Date.now()}@demo.pe`);
  await page.getByLabel(/Contraseña/).first().fill("clave-segura-123");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page).toHaveURL(/\/app$/);
  await page.getByRole("link", { name: "Chat asistente", exact: true }).first().click();
  await expect(page.getByRole("heading", { name: "Chatea con tu asistente de edición" })).toBeVisible();
  await expect(page.getByText(/no está configurada/)).toBeVisible();
  await page.getByLabel("Escribe tu mensaje").fill("Tengo un lunar en la mejilla");
  await page.getByRole("button", { name: "Enviar mensaje" }).click();
  await expect(page.getByText("Tengo un lunar en la mejilla")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Reparar una mancha localizada" })).toBeVisible();
  await page.getByRole("link", { name: /Abrir herramienta: Quitar lunar/ }).click();
  await expect(page).toHaveURL(/\/app\/estudio\?tool=quitar_lunar$/);
  expect(errors).toEqual([]);
});
