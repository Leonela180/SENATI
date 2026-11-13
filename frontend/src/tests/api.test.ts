import { api, ApiError } from "@/lib/api";

test("api convierte el error del servidor en un mensaje legible", async () => {
  // Cada llamada recibe una respuesta nueva (el cuerpo de una Response solo se puede leer una vez)
  globalThis.fetch = vi.fn().mockImplementation(async () => new Response(
    JSON.stringify({ data: null, error: { code: "credenciales", message: "Correo o contraseña incorrectos." } }),
    { status: 401 }));
  await expect(api("/auth/me")).rejects.toThrow(ApiError);
  await expect(api("/auth/me")).rejects.toThrow("Correo o contraseña incorrectos.");
});

test("api envía el token CSRF en las escrituras", async () => {
  const calls: { url: string; headers: Headers }[] = [];
  globalThis.fetch = vi.fn().mockImplementation(async (url: string, init?: RequestInit) => {
    calls.push({ url, headers: new Headers(init?.headers) });
    const body = url.endsWith("/auth/csrf") ? { data: { csrf_token: "tok-123" }, error: null } : { data: { ok: true }, error: null };
    return new Response(JSON.stringify(body), { status: 200 });
  });
  await api("/auth/logout", { method: "POST" });
  const post = calls.find((c) => c.url.endsWith("/auth/logout"))!;
  expect(post.headers.get("X-CSRFToken")).toBe("tok-123");
});
