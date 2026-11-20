import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight, BadgeCheck, CalendarClock, Download, Eraser, FileCheck2, Images, Lock, MessageCircle, Palette,
  RotateCcw, ShieldCheck, Sparkles, Upload, Users, Wand2, X, Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";
import { useHealth } from "@/features/jobs/useJobs";

/** Ejemplo real de la portada, preparado con backend/tools/preparar_portada.py (si no existe, se muestran capturas de la app). */
type Demo = { before: string; after: string; caption: string; beforeLabel?: string; afterLabel?: string };
/** Ejemplos reales por herramienta, preparados con backend/tools/preparar_ejemplos.py. */
type Ejemplo = { tool: string; title: string; text: string; before: string; after: string; caption: string };

const HERRAMIENTAS = [
  { icon: Sparkles, t: "Humanización y textura de piel", d: "Ajusta microtextura y realza reflejos existentes en los ojos. Compara el cambio, que puede ser sutil según el retrato." },
  { icon: RotateCcw, t: "Restauración de fotos", d: "Reduce el ruido, recupera tonos y repara rayas o manchas pequeñas que marques." },
  { icon: Eraser, t: "Quitar lunares y manchas", d: "Haz clic sobre la zona y se rellena con la piel de alrededor." },
  { icon: Palette, t: "Cambiar el fondo", d: "La IA recorta a la persona: fondo de color, desenfocado o transparente." },
  { icon: Wand2, t: "Resolución ×2 y ×4", d: "Amplía hasta 4096 px, reduce ruido y ajusta nitidez, luz y color. Es ampliación digital; no recupera detalle inexistente." },
  { icon: Images, t: "Galería y lotes", d: "Sube varias imágenes, ordénalas en álbumes y procésalas todas a la vez." },
  { icon: MessageCircle, t: "Asistente flotante", d: "Abre la ayuda desde el botón movible sin salir de tu trabajo. Gemini conversa con consentimiento y cuota; la guía local funciona como alternativa." },
  { icon: Users, t: "Equipos y supervisión", d: "El creador es líder del equipo: invita integrantes y revisa sus solicitudes de permiso. Comparte únicamente las imágenes que elijas." },
  { icon: Palette, t: "Tu espacio personalizado", d: "Avatar de iniciales o iconos, temas y colores de acento guardados en este navegador." },
  { icon: FileCheck2, t: "Historial y trazabilidad", d: "Consulta estados y parámetros, compara el original y vuelve por tus resultados aunque cierres la pestaña. El servidor debe seguir encendido." },
  { icon: CalendarClock, t: "Horario y horas", d: "Marca entrada y salida, mira tus horas por recuperar y exporta el reporte." },
];

const PASOS = [
  { icon: Upload, t: "Sube", d: "JPG, PNG o WebP de hasta 10 MB." },
  { icon: FileCheck2, t: "Confirma", d: "Confirmas tu permiso de uso y la autorización de las personas que aparezcan." },
  { icon: Zap, t: "Procesa", d: "El servidor trabaja en segundo plano; puedes seguir navegando." },
  { icon: Download, t: "Compara y descarga", d: "Desliza entre antes y después y descarga el resultado rotulado." },
];

const FAQ = [
  { q: "¿Dónde se procesan mis imágenes?", a: "La edición se realiza en la computadora que aloja LUMIA. Si entras desde otro dispositivo, tus imágenes se suben a ese servidor. Las descripciones de Generar y los mensajes del chat con IA se envían a Google solo con tu consentimiento; el chat no envía tus fotos." },
  { q: "¿El resultado deja de ser una imagen de IA?", a: "No. Sigue siendo una imagen sintética editada: se descarga rotulada «editado con IA» y conserva sus metadatos de procedencia." },
  { q: "¿Cambia el rostro de la persona?", a: "La edición es de baja intensidad para conservar la identidad, la pose, la ropa y el fondo. Siempre puedes comparar y quedarte con el original." },
  { q: "¿Puedo restaurar una fotografía antigua?", a: "Sí: reduce ruido, recupera tonos y repara daños pequeños que marques. No reconstruye información perdida ni colorea automáticamente." },
  { q: "¿Qué pasa si cierro la pestaña?", a: "El trabajo sigue en el servidor. Cuando vuelvas, lo encuentras en el Historial." },
  { q: "¿Necesito una tarjeta gráfica?", a: "El Estudio funciona en CPU. La humanización local necesita pesos instalados y suficiente RAM disponible; su rendimiento depende de la computadora. Los modos experimentales solo se habilitan después de validarlos en el servidor." },
];

function useDemo() {
  const [demo, setDemo] = useState<Demo | null>(null);
  useEffect(() => {
    fetch("/demo/demo.json").then((r) => (r.ok ? r.json() : null)).then((d) => { if (d?.before && d?.after) setDemo(d); }).catch(() => null);
  }, []);
  return demo;
}

function useEjemplos() {
  const [items, setItems] = useState<Ejemplo[]>([]);
  useEffect(() => {
    fetch("/demo/ejemplos.json").then((r) => (r.ok ? r.json() : null))
      .then((d) => { if (Array.isArray(d)) setItems(d.filter((x) => x?.before && x?.after)); }).catch(() => null);
  }, []);
  return items;
}

/** Galería de ejemplos «antes / después»: una pestaña por herramienta. */
function Ejemplos({ items }: { items: Ejemplo[] }) {
  const [i, setI] = useState(0);
  const ex = items[Math.min(i, items.length - 1)];
  return (
    <section id="ejemplos" className="mx-auto max-w-6xl scroll-mt-24 px-4 py-24 md:px-6">
      <div className="mx-auto max-w-2xl space-y-4 text-center">
        <p className="text-xs font-semibold tracking-[0.2em] text-brand-strong uppercase">Ejemplos reales</p>
        <h2 className="font-display text-4xl font-bold text-balance md:text-5xl">Mira la diferencia</h2>
        <p className="text-muted-foreground">Cada ejemplo es el resultado real de la herramienta, sin retoques externos. Desliza para comparar.</p>
      </div>
      <div role="tablist" aria-label="Herramientas" className="mt-10 flex flex-wrap justify-center gap-2">
        {items.map((x, j) => (
          <button key={x.tool + j} role="tab" aria-selected={j === i} onClick={() => setI(j)}
                  className={"rounded-full border px-4 py-2 text-sm transition " + (j === i ? "border-transparent bg-primary text-primary-foreground shadow-sm" : "bg-card hover:bg-accent")}>
            {x.title}
          </button>
        ))}
      </div>
      <div className="mt-10 grid items-center gap-10 lg:grid-cols-[1.3fr_1fr]">
        <BeforeAfterSlider key={ex.after} before={ex.before} after={ex.after} afterLabel="Con LUMIA" />
        <div className="space-y-4">
          <h3 className="font-display text-3xl font-semibold">{ex.title}</h3>
          <p className="text-muted-foreground">{ex.text}</p>
          <p className="rounded-2xl bg-secondary p-4 text-xs text-muted-foreground">{ex.caption}</p>
          <Button asChild className="rounded-full"><Link to="/registro">Probarlo con mi imagen <ArrowRight className="size-4" aria-hidden /></Link></Button>
        </div>
      </div>
    </section>
  );
}

/** Marco de navegador con una captura real de la aplicación. */
function AppShot({ src, alt, className = "" }: { src: string; alt: string; className?: string }) {
  return (
    <div className={`overflow-hidden rounded-2xl border bg-card shadow-xl shadow-black/10 ${className}`}>
      <div className="flex items-center gap-1.5 border-b px-3 py-2">
        <span className="size-2.5 rounded-full bg-red-400/80" /><span className="size-2.5 rounded-full bg-amber-400/80" /><span className="size-2.5 rounded-full bg-emerald-400/80" />
        <span className="ml-3 truncate text-[11px] text-muted-foreground">localhost:5000</span>
      </div>
      <img src={src} alt={alt} loading="lazy" className="block w-full" />
    </div>
  );
}

export default function Home() {
  const { data: health } = useHealth();
  const herramientas = health?.realistic_available ? [...HERRAMIENTAS, { icon: Wand2, t: "De personaje a retrato", d: "Reinterpreta ilustraciones de personajes adultos como retratos sintéticos. Motor local experimental, con filtros y comparación del resultado." }] : HERRAMIENTAS;
  const demo = useDemo();
  const todosLosEjemplos = useEjemplos();
  const ejemplos = todosLosEjemplos.filter(item => item.tool !== "realista" || health?.realistic_available);
  return (
    <>
      {/* ---------- Portada ---------- */}
      <section className="relative overflow-hidden">
        <div aria-hidden className="aurora absolute inset-0" />
        <div className="relative mx-auto max-w-6xl px-4 pt-16 pb-20 text-center md:px-6 lg:pt-24">
          <p className="mx-auto inline-flex items-center gap-2 rounded-full border bg-card px-3.5 py-1.5 text-xs font-medium shadow-sm">
            <Sparkles className="size-3.5 text-brand-strong" aria-hidden /> Estudio de imágenes con IA local
          </p>
          <h1 className="font-display mx-auto mt-6 max-w-4xl text-5xl leading-[1.05] font-bold text-balance md:text-7xl">
            Tus retratos de IA, <span className="text-gradient">más reales.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground md:text-xl">
            Humaniza, restaura y mejora tus fotos en un solo lugar. Piel natural, mejor calidad y fondos limpios,
            conservando siempre tu original.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Button size="lg" asChild className="h-12 rounded-full px-8 text-base">
              <Link to="/registro">Empezar gratis <ArrowRight className="size-4" aria-hidden /></Link>
            </Button>
            <Button size="lg" variant="outline" asChild className="h-12 rounded-full bg-card px-8 text-base">
              <a href={ejemplos.length ? "#ejemplos" : "#herramientas"}>{ejemplos.length ? "Ver ejemplos" : "Ver herramientas"}</a>
            </Button>
          </div>

          <div className="relative mx-auto mt-16 max-w-4xl">
            {demo ? (
              <div className="space-y-3">
                <BeforeAfterSlider before={demo.before} after={demo.after} beforeLabel={demo.beforeLabel || "Generado con IA"} afterLabel={demo.afterLabel || "Humanizado en LUMIA"} />
                <p className="text-xs text-muted-foreground">{demo.caption}</p>
              </div>
            ) : (
              <AppShot src="/showcase/estudio.webp" alt="Estudio de edición de LUMIA AI" />
            )}
          </div>

          <dl className="mx-auto mt-14 grid max-w-2xl grid-cols-3 gap-4">
            {[[String(herramientas.length), "funciones"], ["CPU", "edición local"], ["Original", "siempre conservado"]].map(([n, l]) => (
              <div key={l}><dt className="sr-only">{l}</dt><dd className="font-display text-3xl font-bold text-brand-strong">{n}</dd><p className="text-xs text-muted-foreground">{l}</p></div>
            ))}
          </dl>
        </div>
      </section>

      {ejemplos.length > 0 && <Ejemplos items={ejemplos} />}

      {/* ---------- Herramientas ---------- */}
      <section id="herramientas" className="mx-auto max-w-6xl scroll-mt-24 px-4 py-24 md:px-6">
        <div className="mx-auto max-w-2xl space-y-4 text-center">
          <p className="text-xs font-semibold tracking-[0.2em] text-brand-strong uppercase">Todo en un estudio</p>
          <h2 className="font-display text-4xl font-bold text-balance md:text-5xl">Lo que puedes hacer con <span className="text-gradient">LUMIA</span></h2>
          <p className="text-muted-foreground">Edición en el servidor, originales privados y herramientas para colaborar. Las integraciones externas y los modos experimentales se identifican por separado.</p>
        </div>
        <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {herramientas.map(({ icon: Icon, t, d }) => (
            <article key={t} className="group relative rounded-3xl border bg-card p-6 transition duration-300 hover:-translate-y-1 hover:shadow-lg">
              <span className="grid size-12 place-items-center rounded-2xl bg-brand-soft text-brand-strong transition group-hover:scale-105"><Icon className="size-6" aria-hidden /></span>
              <h3 className="mt-5 text-lg font-semibold">{t}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{d}</p>
            </article>
          ))}
        </div>
        <p className="mt-6 text-center text-xs text-muted-foreground">Opcional: «Generar con IA» usa Gemini de Google y requiere una clave con cuota disponible.</p>
      </section>

      {/* ---------- Cómo funciona ---------- */}
      <section id="como-funciona" className="relative scroll-mt-24 overflow-hidden border-y">
        <div aria-hidden className="absolute inset-0 bg-secondary/60" />
        <div className="relative mx-auto max-w-6xl px-4 py-24 md:px-6">
          <div className="max-w-2xl space-y-4">
            <p className="text-xs font-semibold tracking-[0.2em] text-brand-strong uppercase">Cómo funciona</p>
            <h2 className="font-display text-4xl font-bold text-balance md:text-5xl">Cuatro pasos. Cero complicaciones.</h2>
          </div>
          <ol className="mt-14 grid gap-5 md:grid-cols-4">
            {PASOS.map(({ icon: Icon, t, d }, i) => (
              <li key={t} className="relative rounded-3xl border bg-card p-6">
                <span className="font-display absolute top-5 right-6 text-5xl font-bold text-brand-strong opacity-20">{i + 1}</span>
                <span className="grid size-11 place-items-center rounded-2xl border bg-background"><Icon className="size-5 text-brand-strong" aria-hidden /></span>
                <p className="mt-6 text-lg font-semibold">{t}</p>
                <p className="mt-1.5 text-sm text-muted-foreground">{d}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* ---------- Privacidad ---------- */}
      <section id="privacidad" className="mx-auto grid max-w-6xl scroll-mt-24 gap-6 px-4 py-24 md:px-6 lg:grid-cols-2">
        <div className="rounded-3xl border bg-card p-8">
          <span className="grid size-12 place-items-center rounded-2xl bg-brand-soft text-brand-strong"><Lock className="size-6" aria-hidden /></span>
          <h2 className="font-display mt-6 text-3xl font-bold">Privacidad por diseño</h2>
          <ul className="mt-6 space-y-3 text-sm text-muted-foreground">
            {["Solo tú ves tus imágenes, salvo que compartas una con tu equipo.",
              "La edición ocurre en la computadora que aloja LUMIA AI.",
              "El administrador ve métricas, nunca tus fotos.",
              "Cada resultado se rotula «editado con IA» y conserva su procedencia."].map((x) => (
              <li key={x} className="flex gap-3"><BadgeCheck className="mt-0.5 size-4 shrink-0 text-emerald-500" aria-hidden />{x}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-3xl border bg-card p-8">
          <span className="grid size-12 place-items-center rounded-2xl border bg-background"><ShieldCheck className="size-6" aria-hidden /></span>
          <h2 className="font-display mt-6 text-3xl font-bold">Uso responsable</h2>
          <ul className="mt-6 space-y-3 text-sm text-muted-foreground">
            {["No convierte una imagen sintética en la foto de una persona real.",
              "No borra metadatos ni oculta que hubo edición con IA.",
              "No ofrece suplantación de identidad.",
              "No promete reparar manos ni anatomía."].map((x) => (
              <li key={x} className="flex gap-3"><X className="mt-0.5 size-4 shrink-0 text-red-500" aria-hidden />{x}</li>
            ))}
          </ul>
        </div>
      </section>

      {/* ---------- Preguntas ---------- */}
      <section id="preguntas" className="mx-auto max-w-3xl scroll-mt-24 px-4 pb-24 md:px-6">
        <h2 className="font-display text-center text-4xl font-bold">Preguntas frecuentes</h2>
        <div className="mt-10 divide-y rounded-3xl border bg-card">
          {FAQ.map((f) => (
            <details key={f.q} className="group p-6 [&_summary::-webkit-details-marker]:hidden">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-medium">
                {f.q}<span className="text-2xl text-brand-strong transition group-open:rotate-45" aria-hidden>+</span>
              </summary>
              <p className="mt-3 text-sm text-muted-foreground">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* ---------- Llamado final ---------- */}
      <section className="px-4 pb-24 md:px-6">
        <div className="bg-brand-gradient relative mx-auto max-w-6xl overflow-hidden rounded-[2rem] px-8 py-16 text-center text-white">
                    <h2 className="font-display relative text-4xl font-bold text-balance md:text-5xl">Haz que tus imágenes se vean reales</h2>
          <p className="relative mx-auto mt-4 max-w-xl text-white/85">Crea tu cuenta y prueba el estudio completo en minutos.</p>
          <Button size="lg" variant="secondary" asChild className="relative mt-8 h-13 rounded-full bg-white px-8 text-base text-neutral-900 hover:bg-white/90">
            <Link to="/registro">Crear mi cuenta gratis <ArrowRight className="size-4" aria-hidden /></Link>
          </Button>
        </div>
      </section>
    </>
  );
}
