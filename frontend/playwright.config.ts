import { defineConfig } from "@playwright/test";
export default defineConfig({ testDir: "./e2e", timeout: 300_000, use: { baseURL: "http://localhost:5000", screenshot: "on" } });
