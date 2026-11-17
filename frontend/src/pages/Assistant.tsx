import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight, MessageCircle, Send, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/PageHeader";

const RECIPES = [
  { name: "Recuperar una foto antigua", words: /antigu|vieja|restaur|rayad|deterior|descolor|recuerdo/, tool: "restaurar", steps: ["Abre la foto en Restaurar foto. Empieza con recuperación de tonos al 40–60 %.", "Marca solo las rayas o manchas pequeñas. Ajusta el pincel para no tocar ojos ni contornos.", "Compara el resultado y guarda una copia antes de seguir editando."], limit: "La restauración corrige tonos y daños pequeños; no recupera información inexistente ni colorea automáticamente." },
  { name: "Preparar un retrato profesional", words: /fondo|profesional|cv|curricul|recort|transparent/, tool: "cambiar_fondo", steps: ["Selecciona Cambiar fondo y elige un color neutro o transparencia.", "Revisa los bordes del cabello y los hombros antes de descargar.", "Guarda el resultado y aplica Ajustes si necesitas corregir la luz."], limit: "Los cabellos finos y fondos complejos pueden necesitar otra fotografía." },
  { name: "Reparar una mancha localizada", words: /lunar|mancha|grano|borrar|quitar/, tool: "quitar_lunar", steps: ["Elige Quitar lunar y marca el centro de la mancha.", "Usa un pincel apenas mayor que la zona; evita cubrir rasgos completos.", "Aplica y compara la textura con la piel de alrededor."], limit: "El relleno utiliza píxeles vecinos. No es apropiado para eliminar objetos grandes." },
  { name: "Conseguir efecto retrato", words: /desenfo|gaus|bokeh|retrato/, tool: "desenfoque", steps: ["Selecciona Desenfoque y la zona Fondo.", "Empieza con un radio de 4–8 y conserva el rostro enfocado.", "Revisa la separación entre persona y fondo en la comparación."], limit: "Desenfocar una foto no permite recuperar después sus detalles perdidos." },
  { name: "Mejorar una imagen con ruido", words: /ruido|pixel|nitid|calidad|resoluc|borros/, tool: "mejorar_calidad", steps: ["Activa Reducir ruido en Mejorar calidad.", "Usa nitidez moderada para evitar bordes artificiales.", "Elige doble resolución solo si necesitas un archivo más grande."], limit: "El escalado amplía la imagen; no garantiza recuperar detalles que no estaban en el original." },
  { name: "Corregir luz y color", words: /luz|oscura|brillo|color|contraste|satur/, tool: "ajustes", steps: ["Abre Ajustes y corrige primero el brillo.", "Modifica contraste y saturación en pasos pequeños.", "Comprueba que piel, blancos y sombras mantengan un aspecto natural."], limit: "Las zonas completamente blancas o negras pueden carecer de detalle recuperable." },
];
type Recipe = typeof RECIPES[number];
type Message = { text: string; recipe?: Recipe };

export default function Assistant() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  function ask(text: string) {
    if (!text.trim()) return;
    const normalized = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    const recipe = RECIPES.find(r => r.words.test(normalized));
    setMessages(previous => [...previous.slice(-18), { text: text.trim(), recipe }]);
    setInput("");
  }
  return <div className="mx-auto max-w-5xl space-y-8">
    <PageHeader eyebrow="LUMIA te guía" title="De una foto a un resultado" description="Cuéntanos qué quieres mejorar y encuentra un recorrido concreto por las herramientas del Estudio." />
    <div className="grid gap-6 lg:grid-cols-[18rem_minmax(0,1fr)]">
      <aside className="space-y-4 rounded-3xl border bg-card p-5 lg:self-start">
        <p className="font-display text-xl font-semibold">Elige un objetivo</p>
        {RECIPES.map(r => <button key={r.tool} onClick={() => ask(r.name)} className="flex w-full items-center justify-between gap-2 rounded-xl border p-3 text-left text-sm transition hover:bg-muted">{r.name}<ArrowUpRight className="size-4 shrink-0" aria-hidden /></button>)}
        <p className="flex gap-2 text-xs leading-relaxed text-muted-foreground"><ShieldCheck className="size-4 shrink-0" aria-hidden />Guía local basada en recorridos preparados. No utiliza un modelo de chat, no envía fotos a terceros y no necesita saldo de API.</p>
      </aside>
      <section className="min-w-0 space-y-5 rounded-3xl border bg-card p-5 sm:p-7">
        <div className="flex gap-3"><MessageCircle className="size-6 shrink-0 text-brand-strong" aria-hidden /><p className="text-sm leading-relaxed">Puedo orientarte para restaurar una foto deteriorada, preparar un retrato o corregir ruido y color. Describe un objetivo por mensaje.</p></div>
        <div className="max-h-[60vh] space-y-5 overflow-y-auto" aria-live="polite" aria-relevant="additions">
          {messages.map((m, i) => <div key={i} className="space-y-3">
            <p className="ml-8 rounded-2xl bg-muted px-4 py-3 text-sm"><span className="font-semibold">Tú: </span>{m.text}</p>
            <div className="space-y-3 rounded-2xl border p-4 text-sm leading-relaxed">
              {m.recipe ? <><h2 className="font-semibold">{m.recipe.name}</h2><ol className="list-decimal space-y-2 pl-5">{m.recipe.steps.map(s => <li key={s}>{s}</li>)}</ol><p className="text-xs text-muted-foreground">{m.recipe.limit}</p><Button asChild variant="outline" className="rounded-full"><Link to={`/app/estudio?tool=${m.recipe.tool}`}>Abrir herramienta<ArrowUpRight className="size-4" aria-hidden /></Link></Button></> : <p>No encontré un recorrido para ese objetivo. Elige una opción de la lista o prueba con «restaurar foto antigua», «cambiar fondo» o «reducir ruido». Esta guía no analiza el contenido de tus imágenes.</p>}
            </div>
          </div>)}
        </div>
        <form onSubmit={e => { e.preventDefault(); ask(input); }} className="flex gap-2 border-t pt-5">
          <label htmlFor="assistant-message" className="sr-only">Qué quieres mejorar</label>
          <input id="assistant-message" value={input} onChange={e => setInput(e.target.value)} maxLength={500} placeholder="Quiero recuperar una foto vieja…" className="min-w-0 flex-1 rounded-xl border bg-background px-3 py-3 text-sm" />
          <Button type="submit" disabled={!input.trim()} className="h-auto rounded-xl" aria-label="Consultar guía"><Send className="size-4" aria-hidden /></Button>
        </form>
      </section>
    </div>
  </div>;
}
