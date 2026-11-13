/// <reference types="vitest/config" />
import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  server: { proxy: { "/api": "http://localhost:5000" } },   // mismo origen: las cookies funcionan
  test: { environment: "jsdom", globals: true, setupFiles: "./src/tests/setup.ts", include: ["src/**/*.test.{ts,tsx}"] },
});
