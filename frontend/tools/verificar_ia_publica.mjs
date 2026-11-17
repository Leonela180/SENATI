// Prueba manual real autorizada: crea una cuenta de validación y usa el flujo de la web.
import { chromium } from "@playwright/test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const base = (await fs.readFile(path.join(root, "tools/enlace.txt"), "utf8")).replace(/^\uFEFF/, "").trim();
const directory = path.join(root, "private_data/validacion_publica", new Date().toISOString().replace(/[:.]/g, "-"));
await fs.mkdir(directory, { recursive: true });
const browser = await chromium.launch({ channel: "chromium", headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true });
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  const health = (await (await page.request.get(base + "/api/v1/health")).json()).data;
  assert.equal(health.engine, "local");
  assert.equal(health.runtime, "cpp");
  await page.goto(base + "/registro");
  await page.getByLabel("Nombre").fill("Validación IA local");
  await page.getByLabel("Correo").fill(`validacion+${crypto.randomUUID()}@demo.invalid`);
  await page.getByLabel(/^Contrase/).fill(crypto.randomBytes(24).toString("hex"));
  await page.getByRole("button", { name: "Crear cuenta", exact: true }).click();
  await page.waitForURL(/\/app$/);
  await page.goto(base + "/app/humanizar");
  await page.getByLabel("Seleccionar imagen", { exact: true }).setInputFiles(path.join(root, "imagenes_prueba/rostro_original.png"));
  await page.getByLabel(/^Confirmo que la imagen es generada por IA/).check();
  const queued = page.waitForResponse(response => response.url().endsWith("/api/v1/jobs") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Humanizar imagen", exact: true }).click();
  const created = await (await queued).json();
  assert.ok(created.data?.id, "La web no creó el trabajo");
  let job;
  let maxHeartbeat = 0;
  const started = Date.now();
  while (Date.now() - started < 900_000) {
    job = (await (await page.request.get(base + `/api/v1/jobs/${created.data.id}`)).json()).data;
    if (job.status === "failed") throw new Error(job.error_message ?? job.error_code);
    if (job.status === "completed") break;
    const h = (await (await page.request.get(base + "/api/v1/health")).json()).data;
    if (h.worker_seconds_since_beat !== null) maxHeartbeat = Math.max(maxHeartbeat, h.worker_seconds_since_beat);
    await page.waitForTimeout(2000);
  }
  assert.equal(job.status, "completed");
  assert.notEqual(job.model_id, "mock");
  assert.equal(job.parameters.filtro_seguridad, true);
  assert.equal(job.parameters.facial_detail_applied, true);
  assert.equal(job.parameters.eyes_enhanced, 2);
  assert.ok(maxHeartbeat < 30, "El worker aparentó estar caído durante la inferencia");
  const link = page.getByRole("link", { name: "Descargar resultado", exact: true });
  await link.waitFor({ timeout: 15_000 });
  const downloadEvent = page.waitForEvent("download");
  await link.click();
  const download = await downloadEvent;
  const resultPath = path.join(directory, "resultado.png");
  await download.saveAs(resultPath);
  assert.ok((await fs.readFile(resultPath)).includes(Buffer.from("editado con IA")));
  await page.screenshot({ path: path.join(directory, "resultado_web.png"), fullPage: true });
  assert.deepEqual(errors, []);
  const report = { status: "completed", model: job.model_id, parameters: job.parameters, max_heartbeat_seconds: maxHeartbeat,
                   download_labeled: true, javascript_errors: errors.length };
  await fs.writeFile(path.join(directory, "validacion.json"), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  console.log("Evidencia privada:", directory);
} finally {
  await browser.close();
}
