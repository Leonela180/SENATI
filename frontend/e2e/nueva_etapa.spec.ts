import { expect, test, type Page } from "@playwright/test";
import path from "node:path";

async function register(page: Page, prefix: string) {
  await page.goto("/registro");
  await page.getByLabel("Nombre", { exact: true }).fill(prefix);
  await page.getByLabel("Correo", { exact: true }).fill(`${prefix}${Date.now()}@demo.pe`);
  await page.getByLabel(/Contraseña/).fill("clave-segura-123");
  await page.getByRole("button", { name: "Crear cuenta", exact: true }).click();
  await expect(page).toHaveURL(/\/app$/);
}

test("chat flotante movil, minimizable y persistente al navegar", async ({ page }) => {
  await register(page, "flotante");
  await page.getByRole("button", { name: "Abrir asistente", exact: true }).click();
  const chat = page.getByRole("region", { name: "Chat de ayuda LUMIA" });
  await chat.getByLabel("Escribe tu mensaje").fill("Mi foto antigua tiene rayas");
  await chat.getByRole("button", { name: "Enviar mensaje" }).click();
  await expect(chat.getByRole("link", { name: /Abrir herramienta: Restaurar/ })).toBeVisible();
  await page.getByRole("button", { name: "Minimizar chat" }).click();
  await page.getByRole("link", { name: "Perfil", exact: true }).first().click();
  await page.getByRole("button", { name: "Abrir asistente", exact: true }).click();
  await expect(chat.getByText("Mi foto antigua tiene rayas")).toBeVisible();
  await page.getByRole("button", { name: "Minimizar chat" }).click();
  const mover = page.getByRole("button", { name: "Mover asistente" });
  const before = await mover.boundingBox();
  await mover.focus(); await mover.press("ArrowLeft");
  const after = await mover.boundingBox();
  expect(after!.x).toBeLessThan(before!.x);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Abrir asistente", exact: true }).click();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: path.resolve("../docs/evidencias/etapa_20261119/chat_movil.png"), fullPage: true });
});

test("lider revisa permiso solicitado por integrante", async ({ page, browser }) => {
  await register(page, "lider");
  await page.goto("/app/equipo");
  await page.getByLabel("Nombre del equipo").fill("Equipo creativo");
  await page.getByRole("button", { name: "Crear equipo", exact: true }).click();
  await page.getByRole("button", { name: "Generar invitación" }).click();
  const link = await page.getByLabel("Enlace de invitación").inputValue();
  const context = await browser.newContext();
  try {
    const member = await context.newPage();
    await register(member, "integrante");
    await member.goto(link);
    await member.getByRole("button", { name: "Aceptar invitación" }).click();
    await member.getByLabel("Desde", { exact: true }).fill("2026-12-01T09:00");
    await member.getByLabel("Hasta", { exact: true }).fill("2026-12-01T11:00");
    await member.getByLabel("Motivo", { exact: true }).fill("Trámite personal programado");
    await member.getByRole("button", { name: "Solicitar permiso" }).click();
    await expect(member.getByText("Pendiente", { exact: true })).toBeVisible();
    await page.reload();
    await page.getByRole("button", { name: "Aprobar", exact: true }).click();
    await expect(page.getByText("Aprobado", { exact: true })).toBeVisible();
    await page.screenshot({ path: path.resolve("../docs/evidencias/etapa_20261119/lider_permisos.png"), fullPage: true });
    await member.reload();
    await expect(member.getByText("Aprobado", { exact: true })).toBeVisible();
  } finally { await context.close(); }
});

test("calidad x4 y conversion experimental sin simular motor", async ({ page }) => {
  await register(page, "modos");
  await page.goto("/app/calidad");
  await expect(page).toHaveURL(/tool=mejorar_calidad/);
  await page.getByLabel(/Confirmo que tengo permiso/).check();
  await page.getByLabel("Seleccionar imagen").setInputFiles("e2e/fixtures/retrato_prueba.png");
  await page.getByRole("radio", { name: "Ampliar ×4" }).click();
  await page.getByRole("button", { name: "Aplicar", exact: true }).click();
  await expect(page.getByRole("link", { name: "Descargar resultado", exact: true })).toBeVisible({ timeout: 60000 });
  await page.goto("/app/realista");
  await expect(page.getByRole("heading", { name: "Modo experimental" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Crear versión realista" })).toBeDisabled();
});
