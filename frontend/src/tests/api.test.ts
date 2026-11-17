import { api, ApiError, resetCsrf } from "@/lib/api";

beforeEach(() => resetCsrf());
afterEach(() => vi.unstubAllGlobals());

test("api convierte el error del servidor en un mensaje legible", async () => {
  // Cada llamada recibe una respuesta nueva (el cuerpo de una Response solo se puede leer una vez)
  globalThis.fetch = vi.fn().mockImplementation(async () => new Response(
    JSON.stringify({ data: null, error: { code: "credenciales", message: "Correo o contraseña incorrectos." } }),
    { status: 401 }));
  await expect(api("/auth/me")).rejects.toThrow(ApiError);
  await expect(api("/auth/me")).rejects.toThrow("Correo o contraseña incorrectos.");
});

test("una respuesta HTML exitosa produce un error recuperable", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("<html>Proxy</html>", { status: 200 })));
  await expect(api("/jobs")).rejects.toMatchObject({ code: "respuesta_invalida", status: 200 });
});

test("un fallo al obtener CSRF conserva el mensaje y no envía la escritura", async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({
    data: null, error: { code: "mantenimiento", message: "Servicio temporalmente no disponible." },
  }), { status: 503 }));
  vi.stubGlobal("fetch", fetchMock);
  await expect(api("/auth/logout", { method: "POST" })).rejects.toMatchObject({ status: 503, code: "mantenimiento" });
  expect(fetchMock).toHaveBeenCalledTimes(1);
});

test("renueva un CSRF vencido una sola vez y conserva la clave de idempotencia", async () => {
  let tokens = 0;
  const writes: Headers[] = [];
  vi.stubGlobal("fetch", vi.fn().mockImplementation(async (url: string, init?: RequestInit) => {
    if (url.endsWith("/auth/csrf")) return new Response(JSON.stringify({ data: { csrf_token: `token-${++tokens}` }, error: null }));
    writes.push(new Headers(init?.headers));
    return new Response(JSON.stringify({ data: null, error: { code: "csrf", message: "Token vencido" } }), { status: 403 });
  }));
  await expect(api("/jobs", { method: "POST", headers: { "Idempotency-Key": "intencion-123" } })).rejects.toMatchObject({ status: 403 });
  expect(tokens).toBe(2);
  expect(writes.map((h) => h.get("X-CSRFToken"))).toEqual(["token-1", "token-2"]);
  expect(writes.every((h) => h.get("Idempotency-Key") === "intencion-123")).toBe(true);
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
