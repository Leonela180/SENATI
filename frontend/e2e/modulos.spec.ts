import { expect, test, type Page } from "@playwright/test";

async function registrar(page: Page, nombre: string) {
  await page.goto("/registro");
  await page.getByLabel("Nombre").fill(nombre);
  await page.getByLabel("Correo").fill(`e2e+${nombre.toLowerCase()}${Date.now()}@demo.pe`);
  await page.getByLabel(/Contraseña/).fill("clave-segura-123");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page).toHaveURL(/\/app$/);
}

test("galería → estudio (fondo) → seguir editando (desenfoque)", async ({ page }) => {
  await registrar(page, "Estudio");
  await page.goto("/app/galeria");
  await page.getByLabel(/Confirmo que las imágenes que subo/).check();
  await page.getByLabel("Seleccionar imágenes").setInputFiles(["e2e/fixtures/retrato_ilustrado.png", "e2e/fixtures/retrato_prueba.png"]);
  await expect(page.getByText("2 imágenes", { exact: true })).toBeVisible();
  await page.getByRole("link", { name: "Editar en el Estudio" }).first().click();
  await page.getByRole("tab", { name: "Cambiar fondo" }).click();
  await page.getByRole("button", { name: "Aplicar" }).click();
  await expect(page.getByRole("link", { name: "Descargar resultado" })).toBeVisible({ timeout: 60_000 });
  // Una respuesta lenta al guardar no debe permitir editar la imagen anterior
  // mientras está por cambiar la selección de la galería.
  await page.route("**/api/v1/jobs/*/save", async route => {
    await new Promise(resolve => setTimeout(resolve, 700));
    await route.continue();
  });
  await page.getByRole("button", { name: "Seguir editando este resultado" }).click();
  await expect(page.getByRole("tab", { name: "Desenfoque" })).toBeDisabled();
  await page.getByRole("tab", { name: "Desenfoque" }).click();
  await page.getByRole("button", { name: "Aplicar" }).click();
  await expect(page.getByRole("slider", { name: "Comparar antes y después" })).toBeVisible({ timeout: 60_000 });
});

test("horario y horas: horario, entrada y salida", async ({ page }) => {
  await registrar(page, "Horas");
  await page.goto("/app/horas");
  await page.getByRole("button", { name: "Guardar horario" }).click();
  await expect(page.getByText("Horario guardado")).toBeVisible();
  await page.getByRole("button", { name: "Marcar entrada" }).click();
  await expect(page.getByText("Jornada en curso")).toBeVisible();
  await page.getByRole("button", { name: "Marcar salida" }).click();
  await expect(page.getByText("Fuera de jornada")).toBeVisible();
  await expect(page.getByRole("cell", { name: "en curso" })).toHaveCount(0);
});

test("generar por API permanece desactivado en el alcance de texto", async ({ page }) => {
  await registrar(page, "Gemini");
  await page.goto("/app/generar");
  await expect(page.getByText("Generación de imágenes por API desactivada.", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Generar imagen" })).toBeDisabled();
});
