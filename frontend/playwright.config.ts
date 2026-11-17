import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e", timeout: 120_000, workers: 1,
  use: { baseURL: "http://127.0.0.1:5001", channel: "chromium", screenshot: "only-on-failure", trace: "retain-on-failure" },
});
