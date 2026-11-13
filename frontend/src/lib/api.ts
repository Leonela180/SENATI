type Envelope<T> = { data: T | null; error: { code: string; message: string } | null };

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) { super(message); }
}

let csrfToken: string | null = null;
export const resetCsrf = () => { csrfToken = null; };

async function getCsrf(): Promise<string> {
  if (!csrfToken) {
    const r = await fetch("/api/v1/auth/csrf", { credentials: "include" });
    const j = (await r.json()) as Envelope<{ csrf_token: string }>;
    csrfToken = j.data!.csrf_token;
  }
  return csrfToken;
}

export async function api<T>(path: string, opts: RequestInit = {}, retry = true): Promise<T> {
  const method = (opts.method ?? "GET").toUpperCase();
  const headers = new Headers(opts.headers);
  if (method !== "GET") headers.set("X-CSRFToken", await getCsrf());
  if (opts.body && !(opts.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const r = await fetch(`/api/v1${path}`, { ...opts, method, headers, credentials: "include" });
  let j: Envelope<T> | null = null;
  try { j = (await r.json()) as Envelope<T>; } catch { /* respuesta sin JSON */ }
  if (r.status === 403 && j?.error?.code === "csrf" && retry) {   // token renovado tras iniciar sesión
    resetCsrf();
    return api<T>(path, opts, false);
  }
  if (!r.ok || j?.error) {
    throw new ApiError(r.status, j?.error?.code ?? "error", j?.error?.message ?? "No se pudo conectar con el servidor.");
  }
  return j!.data as T;
}
