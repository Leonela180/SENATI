import { expect, test, type Page } from "@playwright/test";
import path from "node:path";

async function register(page: Page, email: string) {
  await page.goto('/registro');
  await page.getByLabel('Nombre', { exact: true }).fill('Estudio SENATI');
  await page.getByLabel('Correo', { exact: true }).fill(email);
  await page.getByLabel(/Contraseña/).fill('clave-segura-123');
  await page.getByRole('button', { name: 'Crear cuenta' }).click();
  await expect(page).toHaveURL(/\/app$/);
}

test('personalizacion persistente y restauracion continua al cambiar de pantalla', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  await register(page, `restaurar${Date.now()}@demo.pe`);
  await page.goto('/app/perfil');
  await page.getByRole('button', { name: 'Oscuro', exact: true }).click();
  await page.getByRole('button', { name: 'Azul marino', exact: true }).click();
  await page.getByRole('button', { name: 'Cámara', exact: true }).click();
  await page.reload();
  await expect(page.locator('html')).toHaveClass(/dark/);
  await expect(page.locator('html')).toHaveAttribute('data-accent', 'ocean');
  await expect(page.getByRole('button', { name: 'Cámara', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await page.screenshot({ path: path.resolve('../docs/evidencias/mejoras_20261116/personalizacion.png'), fullPage: true });
  await page.goto('/app/asistente');
  await page.getByRole('button', { name: 'Recuperar una foto antigua' }).click();
  await page.getByRole('link', { name: /Abrir herramienta/ }).click();
  await page.getByLabel(/Confirmo que tengo permiso/).check();
  await page.getByLabel('Seleccionar imagen').setInputFiles('e2e/fixtures/retrato_prueba.png');
  await expect(page.getByRole('tab', { name: 'Restaurar foto' })).toHaveAttribute('aria-selected', 'true');
  const request = page.waitForResponse(r => r.url().endsWith('/api/v1/jobs') && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Aplicar', exact: true }).click();
  const job = (await (await request).json()).data;
  await page.goto('/app/galeria');
  await page.goto(`/app/trabajos/${job.id}`);
  await page.reload();
  await expect(page.getByRole('link', { name: /Descargar/ }).first()).toBeVisible({ timeout: 60000 });
  await expect(page.getByRole('slider', { name: 'Comparar antes y después' })).toBeVisible();
  expect(errors).toEqual([]);
});

test('invitacion por correo y WhatsApp con registro propio', async ({ page, browser }) => {
  await register(page, `owner${Date.now()}@demo.pe`);
  await page.goto('/app/equipo');
  await page.getByLabel('Nombre del equipo').fill('Estudio de recuerdos');
  await page.getByRole('button', { name: 'Crear equipo', exact: true }).click();
  const email = `invitada${Date.now()}@demo.pe`;
  await page.getByLabel('Nombre de la persona').fill('Nueva integrante');
  await page.getByLabel('Correo de la persona').fill(email);
  await page.getByRole('button', { name: 'Generar invitación' }).click();
  const field = page.getByRole('textbox', { name: 'Enlace de invitación' });
  await expect(field).not.toHaveValue('');
  const link = await field.inputValue();
  await expect(page.getByRole('link', { name: 'Preparar correo' })).toHaveAttribute('href', /^mailto:/);
  await expect(page.getByRole('link', { name: 'WhatsApp' })).toHaveAttribute('href', /^https:\/\/wa.me\//);
  const context = await browser.newContext();
  try {
    const invited = await context.newPage();
    await invited.goto(link);
    await invited.getByRole('link', { name: 'Crear mi cuenta' }).click();
    await expect(invited.getByLabel('Correo', { exact: true })).toHaveValue(email);
    await expect(invited.getByLabel('Nombre', { exact: true })).toHaveValue('Nueva integrante');
    await invited.getByLabel(/Contraseña/).fill('mi-clave-segura-123');
    await invited.getByRole('button', { name: 'Crear cuenta' }).click();
    await expect(invited.getByRole('heading', { name: 'Estudio de recuerdos' })).toBeVisible();
    await expect(invited.getByText('Eres integrante del equipo.')).toBeVisible();
  } finally { await context.close(); }
});
