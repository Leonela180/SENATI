import { chromium, expect } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
const folder = new URL('../../docs/evidencias/calidad_natural_20261120/', import.meta.url);
await mkdir(folder, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });
const errors = [];
page.on('pageerror', error => errors.push(error.message));
try {
  await page.goto('http://localhost:5000/demo/comparacion.html');
  const results = [];
  for (const [label, filename, beforeSize, afterSize] of [
    ['Ampliación ×4 · tonos naturales','ampliacion-natural.png',[512,640],[2048,2560]],
    ['Edición natural por etapas','etapas-naturales.png',[640,640],[1280,1280]],
  ]) {
    await page.locator('#example').selectOption({ label });
    await expect(page.locator('#title')).toHaveText(label);
    for (const [id, size] of [['before',beforeSize],['after',afterSize]]) {
      await expect.poll(() => page.locator('#'+id).evaluate(img => img.complete && [img.naturalWidth,img.naturalHeight].join('x'))).toBe(size.join('x'));
    }
    await page.screenshot({ path: fileURLToPath(new URL(filename, folder)), fullPage: true });
    results.push({ label, beforeSize, afterSize, loaded: true });
  }
  if (errors.length) throw new Error('Errores JavaScript');
  await page.goto('http://localhost:5000/demo/comparacion.html?ejemplo=flujo_artesana');
  await expect(page.locator('#title')).toHaveText('Edición natural por etapas');
  await writeFile(new URL('verificacion.json',folder),JSON.stringify({status:'passed',results,errors},null,2));
  console.log('Dos ejemplos naturales cargados; dimensiones y comparador verificados.');
} finally { await browser.close(); }
