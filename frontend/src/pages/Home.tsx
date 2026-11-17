import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight, BadgeCheck, CalendarClock, Download, Eraser, FileCheck2, Images, Lock, MessageCircle, Palette,
  RotateCcw, ShieldCheck, Sparkles, Upload, Users, Wand2, X, Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";

/** Ejemplo real de la portada, preparado con backend/tools/preparar_portada.py (si no existe, se muestran capturas de la app). */
type Demo = { before: string; after: string; caption: string };

const HERRAMIENTAS = [
  { icon: Sparkles, t: "Humanización con IA", d: "Piel con microtextura y ojos con reflejos coherentes en retratos generados por IA." },
  { icon: RotateCcw, t: "Restauración de fotos", d: "Reduce el ruido, recupera tonos y repara rayas o manchas pequeñas que marques." },
  { icon: Eraser, t: "Quitar lunares y manchas", d: "Haz clic sobre la zona y se rellena con la piel de alrededor." },
  { icon: Palette, t: "Cambiar el fondo", d: "La IA recorta a la persona: fondo de color, desenfocado o transparente." },
  { icon: Wand2, t: "Calidad y ajustes", d: "Doble resolución, nitidez, desenfoque gaussiano, luz, color y rotación." },
  { icon: Images, t: "Galería y lotes", d: "Sube varias imágenes, ordénalas en álbumes y procésalas todas a la vez." },
  { icon: MessageCircle, t: "Asistente de edición", d: "Cuéntale qué quieres lograr y te guía paso a paso a la herramienta indicada." },
  { icon: Users, t: "Equipos e invitaciones", d: "Invita por enlace, correo o WhatsApp y comparte solo lo que elijas." },
  { icon: CalendarClock, t: "Horario y horas", d: "Marca entrada y salida, mira tus horas por recuperar y exporta el reporte." },
];

const PASOS = [
  { icon: Upload, t: "Sube", d: "JPG, PNG o WebP de hasta 10 MB." },
  { icon: FileCheck2, t: "Confirma", d: "Declaras que es una imagen generada por IA y que puedes usarla." },
  { icon: Zap, t: "Procesa", d: "El servidor trabaja en segundo plano; puedes seguir navegando." },
  { icon: Download, t: "Compara y descarga", d: "Desliza entre antes y después y descarga el resultado rotulado." },
];

const FAQ = [
  { q: "¿Dónde se procesan mis imágenes?", a: "En la computadora que aloja LUMIA AI. Si entras desde otro dispositivo, la imagen se sube a esa computadora. Solo «Generar con IA» envía tu descripción a Google (Gemini), con tu consentimiento." },
  { q: "¿El resultado deja de ser una imagen de IA?", a: "No. Sigue siendo una imagen sintética editada: se descarga rotulada «editado con IA» y conserva sus metadatos de procedencia." },
  { q: "¿Cambia el rostro de la persona?", a: "La edición es de baja intensidad para conservar la identidad, la pose, la ropa y el fondo. Siempre puedes comparar y quedarte con el original." },
  { q: "¿Puedo restaurar una fotografía antigua?", a: "Sí: reduce ruido, recupera tonos y repara daños pequeños que marques. No reconstruye información perdida ni colorea automáticamente." },
  { q: "¿Qué pasa si cierro la pestaña?", a: "El trabajo sigue en el servidor. Cuando vuelvas, lo encuentras en el Historial." },
  { q: "¿Necesito una tarjeta gráfica?", a: "No. El Estudio funciona en el procesador de cualquier laptop. La humanización con IA es más rápida con NVIDIA, pero también funciona sin ella." },
];

function useDemo() {
  const [demo, setDemo] = useState<Demo | null>(null);
  useEffect(() => {
    fetch("/demo/demo.json").then((r) => (r.ok ? r.json() : null)).then((d) => { if (d?.before && d?.after) setDemo(d); }).catch(() => null);
  }, []);
  return demo;
}

/** Marco de navegador con una captura real de la aplicación. */
function AppShot({ src, alt, className = "" }: { src: string; alt: string; className?: string }) {
  return (
    <div className={`overflow-hidden rounded-2xl border bg-card shadow-2xl shadow-black/40 ${className}`}>
      <div className="flex items-center gap-1.5 border-b px-3 py-2">
        <span className="size-2.5 rounded-full bg-red-400/80" /><span className="size-2.5 rounded-full bg-amber-400/80" /><span className="size-2.5 rounded-full bg-emerald-400/80" />
        <span className="ml-3 truncate text-[11px] text-muted-foreground">localhost:5000</span>
      </div>
      <img src={src} alt={alt} loading="lazy" className="block w-full" />
    </div>
  );
}

export default function Home() {
  const demo = useDemo();
  return (
    <>
      {/* ---------- Portada ---------- */}
      <section className="relative overflow-hidden">
        <div aria-hidden className="aurora absolute inset-0" />
        <div aria-hidden className="grid-lines absolute inset-0" />
        <div className="relative mx-auto grid max-w-6xl items-center gap-14 px-4 pt-14 pb-24 md:px-6 lg:grid-cols-[1.05fr_1fr] lg:pt-24 lg:pb-32">
          <div className="space-y-8">
            <p className="glass inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 text-xs font-medium">
              <span className="bg-brand-gradient grid size-5 place-items-center rounded-full text-white"><Sparkles className="size-3" aria-hidden /></span>
              Estudio de imágenes con IA local
            </p>
            <h1 className="font-display text-5xl leading-[1.02] font-bold text-balance md:text-7xl">
              Tus retratos de IA, <span className="text-gradient shine">más reales.</span>
            </h1>
            <p className="max-w-xl text-lg text-muted-foreground md:text-xl">
              Humaniza, restaura y edita en un solo lugar. Piel natural, ojos con vida y fondos perfectos,
              conservando siempre tu original.
            </p>
            <div className="flex flex-wrap gap-3">
              <Button size="lg" asChild className="h-13 rounded-full px-8 text-base">
                <Link to="/registro">Empezar gratis <ArrowRight className="size-4" aria-hidden /></Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="glass h-13 rounded-full px-8 text-base">
                <a href="#herramientas">Ver herramientas</a>
              </Button>
            </div>
            <dl className="grid max-w-lg grid-cols-3 gap-4 pt-2">
              {[["9", "herramientas"], ["100 %", "en tu PC"], ["S/ 0", "en licencias"]].map(([n, l]) => (
                <div key={l}><dt className="sr-only">{l}</dt><dd className="font-display text-3xl font-bold text-gradient">{n}</dd><p className="text-xs text-muted-foreground">{l}</p></div>
              ))}
            </dl>
          </div>

          <div className="relative mx-auto w-full max-w-lg">
            <div aria-hidden className="bg-brand-gradient absolute -inset-6 rounded-[2.5rem] opacity-30 blur-3xl" />
            {demo ? (
              <div className="relative space-y-3">
                <BeforeAfterSlider before={demo.before} after={demo.after} beforeLabel="Generado con IA" afterLabel="Humanizado en LUMIA" />
                <p className="text-center text-xs text-muted-foreground">{demo.caption}</p>
              </div>
            ) : (
              <div className="relative pb-10">
                <AppShot src="/showcase/estudio.webp" alt="Estudio de edición de LUMIA AI" className="float-slow" />
                <AppShot src="/showcase/panel.webp" alt="Panel de LUMIA AI" className="absolute -bottom-2 -left-8 hidden w-1/2 sm:block" />
              </div>
            )}
          </div>
        </div>
      </section>

      {/* ---------- Herramientas ---------- */}
      <section id="herramientas" className="mx-auto max-w-6xl scroll-mt-24 px-4 py-24 md:px-6">
        <div className="mx-auto max-w-2xl space-y-4 text-center">
          <p className="text-xs font-semibold tracking-[0.2em] text-brand-strong uppercase">Todo en un estudio</p>
          <h2 className="font-display text-4xl font-bold text-balance md:text-5xl">Lo que puedes hacer con <span className="text-gradient">LUMIA</span></h2>
          <p className="text-muted-foreground">Herramientas reales que funcionan en tu computadora, sin pagar por servicios externos.</p>
        </div>
        <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {HERRAMIENTAS.map(({ icon: Icon, t, d }) => (
            <article key={t} className="group relative rounded-3xl border bg-card p-6 transition duration-300 hover:-translate-y-1 hover:glow">
              <span className="bg-brand-gradient grid size-12 place-items-center rounded-2xl text-white shadow-lg transition group-hover:scale-110"><Icon className="size-6" aria-hidden /></span>
              <h3 className="mt-5 text-lg font-semibold">{t}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{d}</p>
            </article>
          ))}
        </div>
        <p className="mt-6 text-center text-xs text-muted-foreground">Opcional: «Generar con IA» usa Gemini de Google y requiere una clave con cuota disponible.</p>
      </section>

      {/* ---------- Cómo funciona ---------- */}
      <section id="como-funciona" className="relative scroll-mt-24 overflow-hidden border-y">
        <div aria-hidden className="aurora absolute inset-0 opacity-60" />
        <div className="relative mx-auto max-w-6xl px-4 py-24 md:px-6">
          <div className="max-w-2xl space-y-4">
            <p className="text-xs font-semibold tracking-[0.2em] text-brand-strong uppercase">Cómo funciona</p>
            <h2 className="font-display text-4xl font-bold text-balance md:text-5xl">Cuatro pasos. Cero complicaciones.</h2>
          </div>
          <ol className="mt-14 grid gap-5 md:grid-cols-4">
            {PASOS.map(({ icon: Icon, t, d }, i) => (
              <li key={t} className="glass relative rounded-3xl border p-6">
                <span className="font-display absolute top-5 right-6 text-5xl font-bold text-gradient opacity-40">{i + 1}</span>
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
        <div className="ring-gradient rounded-3xl p-8">
          <span className="bg-brand-gradient grid size-12 place-items-center rounded-2xl text-white"><Lock className="size-6" aria-hidden /></span>
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
                {f.q}<span className="text-gradient text-2xl transition group-open:rotate-45" aria-hidden>+</span>
              </summary>
              <p className="mt-3 text-sm text-muted-foreground">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* ---------- Llamado final ---------- */}
      <section className="px-4 pb-24 md:px-6">
        <div className="bg-brand-gradient relative mx-auto max-w-6xl overflow-hidden rounded-[2rem] px-8 py-16 text-center text-white">
          <div aria-hidden className="grid-lines absolute inset-0 opacity-40" />
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
