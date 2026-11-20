// Smoke test de una instalacion aislada en puerto 5002; no usa cuentas DEMO.
import { chromium, expect } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
const base = process.env.LUMIA_VALIDATION_URL || 'http://127.0.0.1:5002';
if (!/^http:\/\/(127\.0\.0\.1|localhost):5002$/.test(base)) throw new Error('Este test solo admite el puerto aislado 5002');
const folder = process.env.LUMIA_VALIDATION_EVIDENCE;
if (!folder) throw new Error('Indica una carpeta de evidencia');
await mkdir(folder, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errors = [];
page.on('pageerror', error => errors.push(error.message));
const report = { status: 'pending', checks: [], engine: 'mock', errors };
try {
  await page.goto(base + '/registro');
  await page.getByLabel('Nombre').fill('Validacion de instalacion');
  await page.getByLabel('Correo').fill(`instalacion${Date.now()}@demo.pe`);
  await page.getByLabel(/Contraseña/).fill('Validacion-aislada-2026!');
  await page.getByRole('button', { name: 'Crear cuenta' }).click();
  await expect(page).toHaveURL(/\/app$/);
  report.checks.push('registro y sesion en esquema exclusivo');
  await page.goto(base + '/app/galeria');
  await page.getByLabel(/Confirmo que las imágenes que subo/).check();
  await page.getByLabel('Seleccionar imágenes').setInputFiles(fileURLToPath(new URL('../e2e/fixtures/retrato_prueba.png', import.meta.url)));
  await page.getByRole('link', { name: 'Editar en el Estudio' }).first().click();
  await page.getByRole('tab', { name: 'Cambiar fondo' }).click();
  await page.getByRole('button', { name: 'Aplicar', exact: true }).click();
  await expect(page.getByRole('link', { name: 'Descargar resultado', exact: true })).toBeVisible({ timeout: 120000 });
  await expect(page.getByRole('slider', { name: 'Comparar antes y después' })).toBeVisible();
  const jobs = await (await page.request.get(base + '/api/v1/jobs')).json();
  const job = jobs.data.items[0];
  if (job.tool !== 'cambiar_fondo' || job.status !== 'completed' || job.model_id === 'mock') throw new Error('El Estudio no produjo una edicion real');
  const download = await page.request.get(base + `/api/v1/jobs/${job.id}/download?inline=1`);
  if (download.status() !== 200 || !(await download.body()).subarray(0,4).equals(Buffer.from([137,80,78,71]))) throw new Error('Descarga PNG no valida');
  report.checks.push('carga, segmentacion real, comparacion y descarga PNG');
  await page.screenshot({ path: folder + '/instalacion-editor.png', fullPage: true });
  await page.getByRole('button', { name: 'Abrir asistente', exact: true }).click();
  await page.getByLabel('Escribe tu mensaje').fill('Tengo un lunar en la mejilla');
  await page.getByRole('button', { name: 'Enviar mensaje' }).click();
  await expect(page.getByRole('heading', { name: 'Reparar una mancha localizada' })).toBeVisible();
  report.checks.push('chat flotante y guia local sin API');
  await page.screenshot({ path: folder + '/instalacion-chat.png', fullPage: true });
  const health = await (await page.request.get(base + '/api/v1/health')).json();
  if (health.data.engine !== 'mock' || health.data.worker_seconds_since_beat == null || health.data.worker_seconds_since_beat > 20) throw new Error('Modo o worker inesperado');
  if (errors.length) throw new Error('Errores JavaScript');
  report.status = 'passed';
} catch (error) {
  report.status = 'failed'; report.failure = error.message; throw error;
} finally {
  await writeFile(folder + '/instalacion-runtime.json', JSON.stringify(report, null, 2));
  await browser.close();
}
console.log(JSON.stringify(report));
