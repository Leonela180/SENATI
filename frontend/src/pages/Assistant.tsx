import { useEffect, useId, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, Bot, Loader2, Send, ShieldCheck, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/PageHeader";
import { api } from "@/lib/api";

const RECIPES = [
  { name: "Solicitar o revisar un permiso", words: /permiso|lider|jefe|equipo|invit|grupo/, tool: "equipo", steps: ["Abre Equipo. Quien crea el espacio es su líder dentro de LUMIA.", "Como integrante, indica Desde, Hasta y Motivo en Permisos del equipo.", "El líder revisa y aprueba o rechaza; tú puedes consultar la respuesta o cancelar mientras esté pendiente."], limit: "No verifica cargos legales ni modifica automáticamente tus horas. Solo tú y el líder ven el motivo." },
  { name: "Personalizar mi espacio", words: /avatar|tema|oscuro|claro|personaliz|color de la pagina/, tool: "perfil", steps: ["Abre Perfil y la sección Tu estilo.", "Elige avatar, acento y apariencia; los cambios se aplican al instante.", "Puedes restablecer las preferencias en cualquier momento."], limit: "Las preferencias se guardan en este navegador, no se sincronizan entre dispositivos." },
  { name: "Convertir una ilustración", words: /pixar|disney|ilustr|personaje|convertir|dibujo/, tool: "realista", steps: ["Abre Ilustración a realista en el laboratorio.", "Revisa si el modo está habilitado: necesita una validación de calidad y un motor real compatible.", "Si está disponible, elige un personaje adulto y confirma tu permiso de uso."], limit: "Es experimental y puede cambiar los rasgos. No se garantiza una conversión fiel ni se ofrece mientras esté deshabilitado." },
  { name: "Quitar el aspecto de plástico", words: /plastic|artificial|piel lisa|muy lis|muneca|poros|textura/, tool: "textura_piel", steps: ["Abre el retrato en Textura de piel realista. Empieza con intensidad al 60–70 %.", "Compara con el deslizador: los poros deben verse de cerca, no desde lejos.", "Si quieres más naturalidad, después usa Humanizar o activa las pecas suaves."], limit: "Es un filtro digital: agrega textura a la piel detectada; no cambia la forma del rostro ni corrige la iluminación." },
  { name: "Recuperar una foto antigua", words: /antigu|vieja|restaur|rayad|deterior|descolor|recuerdo/, tool: "restaurar", steps: ["Abre la foto en Restaurar foto. Empieza con recuperación de tonos al 40–60 %.", "Marca solo las rayas o manchas pequeñas. Ajusta el pincel para no tocar ojos ni contornos.", "Compara el resultado y guarda una copia antes de seguir editando."], limit: "La restauración corrige tonos y daños pequeños; no recupera información inexistente ni colorea automáticamente." },
  { name: "Preparar un retrato profesional", words: /fondo|profesional|cv|curricul|recort|transparent/, tool: "cambiar_fondo", steps: ["Selecciona Cambiar fondo y elige un color neutro o transparencia.", "Revisa los bordes del cabello y los hombros antes de descargar.", "Guarda el resultado y aplica Ajustes si necesitas corregir la luz."], limit: "Los cabellos finos y fondos complejos pueden necesitar otra fotografía." },
  { name: "Reparar una mancha localizada", words: /lunar|mancha|grano|borrar|quitar/, tool: "quitar_lunar", steps: ["Elige Quitar lunar y marca el centro de la mancha.", "Usa un pincel apenas mayor que la zona; evita cubrir rasgos completos.", "Aplica y compara la textura con la piel de alrededor."], limit: "El relleno utiliza píxeles vecinos. No es apropiado para eliminar objetos grandes." },
  { name: "Conseguir efecto retrato", words: /desenfo|gaus|bokeh|retrato/, tool: "desenfoque", steps: ["Selecciona Desenfoque y la zona Fondo.", "Empieza con un radio de 4–8 y conserva el rostro enfocado.", "Revisa la separación entre persona y fondo en la comparación."], limit: "Desenfocar una foto no permite recuperar después sus detalles perdidos." },
  { name: "Mejorar una imagen con ruido", words: /ruido|pixel|nitid|calidad|resoluc|borros/, tool: "mejorar_calidad", steps: ["Activa Reducir ruido en Mejorar calidad.", "Usa nitidez moderada para evitar bordes artificiales.", "Elige doble resolución solo si necesitas un archivo más grande."], limit: "El escalado amplía la imagen; no garantiza recuperar detalles que no estaban en el original." },
  { name: "Corregir luz y color", words: /luz|oscura|brillo|color|contraste|satur/, tool: "ajustes", steps: ["Abre Ajustes y corrige primero el brillo.", "Modifica contraste y saturación en pasos pequeños.", "Comprueba que piel, blancos y sombras mantengan un aspecto natural."], limit: "Las zonas completamente blancas o negras pueden carecer de detalle recuperable." },
];
type Recipe = typeof RECIPES[number];
type Msg = { role: "user" | "model"; text: string; tool?: string | null; recipe?: Recipe; source?: "gemini" | "local"; note?: string };

const TOOL_LINKS: Record<string, { label: string; to: string }> = {
  equipo: { label: "Equipo y permisos", to: "/app/equipo" },
  horas: { label: "Horario y horas", to: "/app/horas" },
  perfil: { label: "Personalizar mi espacio", to: "/app/perfil" },
  realista: { label: "Laboratorio realista", to: "/app/realista" },
  humanizar: { label: "Humanizar", to: "/app/humanizar" },
  galeria: { label: "Galería", to: "/app/galeria" },
  generar: { label: "Generar con IA", to: "/app/generar" },
  restaurar: { label: "Restaurar foto", to: "/app/estudio?tool=restaurar" },
  quitar_lunar: { label: "Quitar lunar", to: "/app/estudio?tool=quitar_lunar" },
  cambiar_fondo: { label: "Cambiar fondo", to: "/app/estudio?tool=cambiar_fondo" },
  desenfoque: { label: "Desenfoque", to: "/app/estudio?tool=desenfoque" },
  mejorar_calidad: { label: "Mejorar calidad", to: "/app/estudio?tool=mejorar_calidad" },
  ajustes: { label: "Ajustes", to: "/app/estudio?tool=ajustes" },
  textura_piel: { label: "Textura de piel", to: "/app/estudio?tool=textura_piel" },
};
const SUGERENCIAS = ["Mi foto antigua tiene rayas y está opaca", "Quiero un fondo blanco para mi CV", "Tengo un lunar en la mejilla", "Mi retrato de IA se ve muy plástico"];
const CONSENT_KEY = "lumia-chat-consentimiento";

function localAnswer(text: string): Msg {
  const normalized = text.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const recipe = RECIPES.find(r => r.words.test(normalized));
  return recipe
    ? { role: "model", text: recipe.name, recipe, tool: recipe.tool, source: "local" }
    : { role: "model", source: "local", text: "No encontré un recorrido para eso. Prueba con «restaurar foto antigua», «cambiar fondo», «quitar lunar» o «reducir ruido», o elige un objetivo de la lista." };
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
            <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-secondary px-4 py-3 text-sm leading-relaxed">¡Hola! Soy el asistente de LUMIA. Dime qué quieres mejorar en tu foto y te digo cómo hacerlo.</div></div>
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
