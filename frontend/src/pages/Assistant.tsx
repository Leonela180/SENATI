import { useEffect, useId, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, Bot, Loader2, Send, ShieldCheck, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/PageHeader";
import { api } from "@/lib/api";
import { BIENVENIDA, RECIPES, SIN_COINCIDENCIA, SUGERENCIAS, TOOL_LINKS, buscarReceta, type Recipe } from "@/features/assistant/guiaLocal";

// MÓDULO CHATBOT · Pantalla del asistente (también se usa dentro del chat flotante, modo compact).
// Preguntas y respuestas sin IA: features/assistant/guiaLocal.ts · Instrucciones para Gemini: backend/app/services/asistente_instrucciones.py

type Msg = { role: "user" | "model"; text: string; tool?: string | null; recipe?: Recipe; source?: "gemini" | "local"; note?: string };

const CONSENT_KEY = "lumia-chat-consentimiento";

function localAnswer(text: string): Msg {
  const recipe = buscarReceta(text);
  return recipe
    ? { role: "model", text: recipe.name, recipe, tool: recipe.tool, source: "local" }
    : { role: "model", source: "local", text: SIN_COINCIDENCIA };
}

export default function Assistant({ compact = false }: { compact?: boolean } = {}) {
  const fieldId = useId();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [busy, setBusy] = useState(false);
  const [consent, setConsent] = useState(() => { try { return localStorage.getItem(CONSENT_KEY) === "si"; } catch { return false; } });
  const status = useQuery({ queryKey: ["assistant-status"], queryFn: () => api<{ configured: boolean; model: string }>("/assistant/status") });
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => { end.current?.scrollIntoView?.({ behavior: "smooth", block: "end" }); }, [messages, busy]);
  const aiReady = consent && !!status.data?.configured;

  function toggleConsent(v: boolean) {
    setConsent(v);
    try { localStorage.setItem(CONSENT_KEY, v ? "si" : "no"); } catch { /* sin almacenamiento: solo esta sesión */ }
  }

  async function ask(text: string) {
    const clean = text.trim();
    if (!clean || busy) return;
    const history = [...messages, { role: "user" as const, text: clean }].slice(-24);
    setMessages(history);
    setInput("");
    if (!aiReady) { setMessages([...history, localAnswer(clean)]); return; }
    setBusy(true);
    try {
      const r = await api<{ reply: string; tool: string | null }>("/assistant/chat", {
        method: "POST",
        body: JSON.stringify({ consent: true, messages: history.map(m => ({ role: m.role, text: m.recipe ? m.recipe.steps.join(" ") : m.text })) }),
      });
      setMessages([...history, { role: "model", text: r.reply, tool: r.tool, source: "gemini" }]);
    } catch (e) {
      setMessages([...history, { ...localAnswer(clean), note: `${(e as Error).message} Te respondo con la guía local.` }]);
    } finally { setBusy(false); }
  }

  return <div className={compact ? "h-full overflow-y-auto" : "mx-auto max-w-5xl space-y-8"}>
    {!compact && <PageHeader eyebrow="Asistente LUMIA" title="Chatea con tu asistente de edición" description="Cuéntale qué quieres lograr con tu foto: te explica los pasos y te lleva a la herramienta indicada." />}
    <div className={compact ? "space-y-2" : "grid gap-6 lg:grid-cols-[18rem_minmax(0,1fr)]"}>
      <aside className={compact ? "space-y-2 px-4 py-2" : "space-y-4 rounded-3xl border bg-card p-5 lg:self-start"}>
        <p className="font-display text-lg font-semibold">Objetivos rápidos</p>
        {!compact && RECIPES.map(r => <button key={r.tool} onClick={() => void ask(r.name)} className="flex w-full items-center justify-between gap-2 rounded-xl border p-3 text-left text-sm transition hover:bg-muted">{r.name}<ArrowUpRight className="size-4 shrink-0" aria-hidden /></button>)}
        <div className="space-y-2 rounded-2xl bg-secondary p-4 text-xs leading-relaxed">
          <label className="flex items-start gap-2 font-medium">
            <input type="checkbox" checked={consent} onChange={e => toggleConsent(e.target.checked)} className="mt-0.5" />
            Usar IA (Gemini) para conversar
          </label>
          <p className="text-muted-foreground">Solo se envía el <b>texto</b> que escribes a Google; nunca tus imágenes. Sin esta opción, responde la guía local.</p>
          {status.data && !status.data.configured && <p className="text-amber-700 dark:text-amber-300">La IA del chat no está configurada (falta la clave de Gemini en el .env). Responde la guía local.</p>}
        </div>
        <p className="flex gap-2 text-xs leading-relaxed text-muted-foreground"><ShieldCheck className="size-4 shrink-0" aria-hidden />Las conversaciones no se guardan.</p>
      </aside>

      <section className="flex min-w-0 flex-col rounded-3xl border bg-card">
        <div className="flex items-center gap-3 border-b px-5 py-4">
          <span className="grid size-10 place-items-center rounded-full bg-brand-soft text-brand-strong"><Bot className="size-5" aria-hidden /></span>
          <div><p className="font-semibold">Asistente LUMIA</p>
            <p className="text-xs text-muted-foreground">{aiReady ? "Conversación con IA (Gemini)" : "Guía local"}</p></div>
        </div>
        <div className={compact ? "h-64 space-y-4 overflow-y-auto p-4" : "min-h-[24rem] flex-1 space-y-4 overflow-y-auto p-5 sm:max-h-[60vh]"} aria-live="polite" aria-relevant="additions">
          <div className="flex gap-3"><span className="grid size-8 shrink-0 place-items-center rounded-full bg-brand-soft text-brand-strong"><Sparkles className="size-4" aria-hidden /></span>
            <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-secondary px-4 py-3 text-sm leading-relaxed">{BIENVENIDA}</div></div>
          {messages.length === 0 && <div className="flex flex-wrap gap-2 pl-11">{SUGERENCIAS.map(s => <button key={s} onClick={() => void ask(s)} className="rounded-full border bg-background px-3 py-1.5 text-xs transition hover:bg-accent">{s}</button>)}</div>}
          {messages.map((m, i) => m.role === "user"
            ? <div key={i} className="flex justify-end"><p className="max-w-[85%] rounded-2xl rounded-tr-sm bg-primary px-4 py-3 text-sm text-primary-foreground"><span className="sr-only">Tú: </span>{m.text}</p></div>
            : <div key={i} className="flex gap-3"><span className="grid size-8 shrink-0 place-items-center rounded-full bg-brand-soft text-brand-strong"><Sparkles className="size-4" aria-hidden /></span>
                <div className="max-w-[85%] space-y-3 rounded-2xl rounded-tl-sm bg-secondary px-4 py-3 text-sm leading-relaxed">
                  {m.note && <p className="text-xs text-amber-700 dark:text-amber-300">{m.note}</p>}
                  {m.recipe ? <><h2 className="font-semibold">{m.recipe.name}</h2><ol className="list-decimal space-y-1.5 pl-5">{m.recipe.steps.map(s => <li key={s}>{s}</li>)}</ol><p className="text-xs text-muted-foreground">{m.recipe.limit}</p></>
                    : <p className="whitespace-pre-line">{m.text}</p>}
                  {m.tool && TOOL_LINKS[m.tool] && <Button asChild size="sm" variant="outline" className="rounded-full bg-card"><Link to={TOOL_LINKS[m.tool].to}>Abrir herramienta: {TOOL_LINKS[m.tool].label}<ArrowUpRight className="size-4" aria-hidden /></Link></Button>}
                  <p className="text-[10px] tracking-wide text-muted-foreground uppercase">{m.source === "gemini" ? "Respuesta generada con IA" : "Guía local"}</p>
                </div></div>)}
          {busy && <div className="flex items-center gap-2 pl-11 text-xs text-muted-foreground"><Loader2 className="size-4 animate-spin" aria-hidden />Escribiendo…</div>}
          <div ref={end} />
        </div>
        <form onSubmit={e => { e.preventDefault(); void ask(input); }} className="flex gap-2 border-t p-4">
          <label htmlFor={fieldId} className="sr-only">Escribe tu mensaje</label>
          <input id={fieldId} value={input} onChange={e => setInput(e.target.value)} maxLength={1000} placeholder="Escribe tu mensaje…" className="min-w-0 flex-1 rounded-full border bg-background px-4 py-3 text-sm" />
          <Button type="submit" disabled={!input.trim() || busy} className="size-11 rounded-full p-0" aria-label="Enviar mensaje"><Send className="size-4" aria-hidden /></Button>
        </form>
      </section>
    </div>
  </div>;
}
