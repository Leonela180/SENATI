// Comprueba la API real y el túnel con cuentas DEMO. Nunca imprime contraseñas.
import { chromium, expect } from '@playwright/test';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
const root = new URL('../../', import.meta.url);
const state = JSON.parse(await readFile(new URL('private_data/demo_senati/accesos_y_avance.json', root), 'utf8'));
const base = (await readFile(new URL('tools/enlace.txt', root), 'utf8')).trim();
if (!/^https:\/\/[a-z0-9-]+\.trycloudflare\.com$/.test(base)) throw new Error('Enlace inesperado');
const evidence = new URL('docs/evidencias/cierre_20261120/', root);
await mkdir(evidence, { recursive: true });
const browser = await chromium.launch({ headless: true });
const errors = [];
const report = { url: base, checks: [], errors };
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(base, { waitUntil: 'networkidle' });
  await expect(page.getByRole('heading', { name: /Mira la diferencia/ })).toHaveCount(1);
  const pictures = page.locator('img');
  await expect(pictures.first()).toBeVisible();
  await page.screenshot({ path: new URL('portada-real.png', evidence).pathname.replace(/^\/(\w:)/, '$1'), fullPage: true });
  report.checks.push('portada HTTPS con ejemplos');
  async function login(slug) {
    const account = state.accounts[slug];
    await page.goto(base + '/login');
    await page.getByLabel('Correo').fill(account.email);
    await page.getByLabel(/Contraseña/).fill(account.password);
    await page.getByRole('button', { name: 'Entrar', exact: true }).click();
    await expect(page).toHaveURL(/\/app$/);
  }
  await login('individual1');
  await page.goto(base + '/app/galeria');
  await expect(page.getByRole('heading', { name: 'Tus imágenes' })).toBeVisible();
  await expect(page.locator('main img').first()).toBeVisible();
  await page.screenshot({ path: new URL('galeria-demo-real.png', evidence).pathname.replace(/^\/(\w:)/, '$1'), fullPage: true });
  const sample = state.accounts.individual1.jobs['0-0'].id;
  await page.goto(base + '/app/trabajos/' + sample);
  await expect(page.getByRole('slider', { name: 'Comparar antes y después' })).toBeVisible();
  report.checks.push('sesion segura, galeria DEMO y comparador de trabajo real');
  await page.getByRole('button', { name: 'Procesar de nuevo', exact: true }).click();
  await expect(page).not.toHaveURL(new RegExp('/trabajos/' + sample + '$'));
  await expect(page).toHaveURL(/\/app\/trabajos\/\d+/);
  const repeatedId = Number(page.url().split('/').at(-1));
  if (repeatedId === sample) throw new Error('No se creo el trabajo repetido');
  const repeated = await (await context.request.get(base + '/api/v1/jobs/' + repeatedId)).json();
  if (repeated.data.tool !== 'cambiar_fondo') throw new Error('El reintento cambio de herramienta');
  await expect(page.getByRole('slider', { name: 'Comparar antes y después' })).toBeVisible({ timeout: 60000 });
  report.checks.push('repeticion real conserva herramienta y completa resultado');
  await page.getByRole('button', { name: 'Abrir asistente', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Minimizar chat' })).toBeVisible();
  report.checks.push('asistente flotante');
  await page.getByRole('button', { name: 'Salir', exact: true }).click();
  await login('grupo1-lider');
  await page.goto(base + '/app/equipo');
  await expect(page.getByText('DEMO · Aurora Retratos', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Avance por integrante' })).toBeVisible();
  await page.screenshot({ path: new URL('equipo-demo-real.png', evidence).pathname.replace(/^\/(\w:)/, '$1'), fullPage: true });
  report.checks.push('lider, integrantes y permisos del grupo DEMO');
  const health = await (await context.request.get(base + '/api/v1/health')).json();
  if (health.data.status !== 'ok' || health.data.worker_seconds_since_beat > 20 || health.data.worker_seconds_since_beat == null) throw new Error('Worker sin latido reciente');
  report.health = health.data;
  if (health.data.realistic_available) {
    await page.goto(base + '/app/realista');
    await expect(page.getByLabel('Representación del personaje')).toBeVisible();
    report.checks.push('laboratorio disponible con selector de personaje');
  }
  if (errors.length) throw new Error('Errores JavaScript en el navegador');
  report.status = 'passed';
} catch (error) {
  report.status = 'failed';
  report.failure = error.message;
  throw error;
} finally {
  await writeFile(new URL('publico-real.json', evidence), JSON.stringify(report, null, 2));
  await browser.close();
}
console.log(JSON.stringify(report));
