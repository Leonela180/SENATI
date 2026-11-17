import { useSyncExternalStore } from "react";

export const ACCENTS = { violet: "Aurora", copper: "Atardecer", ocean: "Océano", forest: "Esmeralda" } as const;
export const AVATARS = { initials: "Iniciales", camera: "Cámara", spark: "Destello", leaf: "Hoja", mountain: "Montaña" } as const;
type Appearance = { mode: "light" | "dark" | "system"; accent: keyof typeof ACCENTS; avatar: keyof typeof AVATARS; compact: boolean };
const defaults: Appearance = { mode: "dark", accent: "violet", avatar: "initials", compact: false };
let current = defaults;
try {
  const value = JSON.parse(localStorage.getItem("lumia-appearance") || "{}");
  current = { mode: ["light", "dark", "system"].includes(value.mode) ? value.mode : defaults.mode,
    accent: Object.prototype.hasOwnProperty.call(ACCENTS, value.accent) ? value.accent : defaults.accent,
    avatar: Object.prototype.hasOwnProperty.call(AVATARS, value.avatar) ? value.avatar : defaults.avatar,
    compact: value.compact === true };
} catch { /* Navegacion privada o preferencias antiguas: usar valores seguros. */ }
const listeners = new Set<() => void>();
const media = window.matchMedia("(prefers-color-scheme: dark)");
function apply() {
  document.documentElement.classList.toggle("dark", current.mode === "dark" || (current.mode === "system" && media.matches));
  document.documentElement.dataset.accent = current.accent;
  document.documentElement.dataset.compact = String(current.compact);
  document.documentElement.style.colorScheme = document.documentElement.classList.contains("dark") ? "dark" : "light";
}
apply();
media.addEventListener("change", apply);
export function updateAppearance(patch: Partial<Appearance>) {
  current = { ...current, ...patch };
  let persisted = true;
  try { localStorage.setItem("lumia-appearance", JSON.stringify(current)); } catch { persisted = false; }
  apply();
  listeners.forEach(listener => listener());
  return persisted;
}
export function useAppearance() {
  return useSyncExternalStore(listener => { listeners.add(listener); return () => { listeners.delete(listener); }; }, () => current);
}
