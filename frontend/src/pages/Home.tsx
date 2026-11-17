import { Link } from "react-router-dom";
import {
  ArrowRight, BadgeCheck, Cpu, Download, Eye, FileCheck2, Lock, MonitorSmartphone, ScanFace, ShieldCheck, Sparkles,
  SunMedium, Upload, Users, Wand2, X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";

const SINTOMAS = [
  { t: "Piel de cera", d: "Superficies lisas y brillantes, sin poros ni variaciones de tono." },
  { t: "Mirada sin vida", d: "Ojos sin reflejos coherentes ni detalle en el iris." },
  { t: "Luz imposible", d: "Sombras que no coinciden con ninguna fuente de luz." },
];

const MEJORAS = [
  { kind: "piel" as const, icon: ScanFace, t: "Piel con microtextura", d: "Poros y variaciones sutiles de tono, sin embellecer ni cambiar el color de piel." },
  { kind: "ojos" as const, icon: Eye, t: "Ojos coherentes", d: "Reflejos y detalle del iris que hacen creíble la mirada." },
  { kind: "cabello" as const, icon: Wand2, t: "Edición conservadora", d: "Una mezcla de baja intensidad limita los cambios. Compara siempre los contornos y el cabello." },
  { kind: "luz" as const, icon: SunMedium, t: "Tonos naturales", d: "Ajustes moderados para mantener un aspecto fotográfico. Cada retrato puede responder de forma diferente." },
];

const PASOS = [
  { icon: Upload, t: "Sube tu retrato", d: "Un retrato de persona generado por IA en JPG, PNG o WebP de hasta 10 MB." },
  { icon: FileCheck2, t: "Declara su origen", d: "Confirmas que la imagen es sintética y que tienes permiso para usarla." },
  { icon: Cpu, t: "El servidor trabaja", d: "La imagen se procesa en segundo plano. Puedes cambiar de pantalla y volver desde el historial." },
  { icon: Download, t: "Compara y descarga", d: "Deslizas entre el antes y el después y descargas el resultado rotulado." },
];

const FAQ = [
  { q: "¿Puedo restaurar una fotografía antigua?", a: "Sí, en el Estudio puedes reducir ruido, recuperar tonos y reparar manchas o rayas pequeñas marcadas por ti. No reconstruye información perdida ni colorea automáticamente. Confirma que tienes permiso para editar la foto." },
  { q: "¿El asistente necesita una API de pago?", a: "No. El asistente de edición es una guía local de recorridos preparados que recomienda herramientas. No es un modelo de chat y no analiza tus imágenes." },
  { q: "¿Qué pasa si cierro la pestaña?", a: "El trabajo continúa mientras el servidor permanezca encendido. Puedes consultar su estado y descargar el resultado desde Historial cuando vuelvas a iniciar sesión." },
  { q: "¿Dónde se procesan mis imágenes?", a: "Las imágenes se guardan y editan en la computadora que aloja LUMIA AI. Si accedes desde otro dispositivo, se suben a esa computadora. Generar con IA envía tu descripción a Google (Gemini), con tu consentimiento." },
  { q: "¿El resultado deja de ser una imagen de IA?", a: "No. Sigue siendo una imagen sintética editada. Por eso se descarga rotulada «editado con IA» y conserva los metadatos de procedencia." },
  { q: "¿Cambia el rostro de la persona?", a: "La edición es de baja intensidad para conservar la identidad aparente, la pose, la ropa y el fondo. Si notas cambios, puedes volver a procesar o quedarte con el original." },
  { q: "¿Repara manos o cuerpos completos?", a: "No. LUMIA AI se centra en la apariencia de retratos: piel, ojos, cabello y luz. No corrige anatomía." },
  { q: "¿Puedo trabajar en equipo?", a: "Sí. Puedes crear un equipo, invitar por enlace y compartir solo las imágenes que elijas. El equipo ve estadísticas agregadas." },
];

export default function Home() {
  return (
    <>
      {/* ---------- Portada ---------- */}
      <section className="relative overflow-hidden">
        <div aria-hidden className="absolute top-[-10rem] right-[-12rem] size-[38rem] rounded-full bg-[oklch(0.9_0.05_60/0.6)] blur-3xl" />
        <div className="relative mx-auto grid max-w-6xl items-center gap-14 px-4 pt-12 pb-20 md:px-6 lg:grid-cols-[1.1fr_1fr] lg:pt-20 lg:pb-28">
          <div className="space-y-8">
            <p className="inline-flex items-center gap-2 rounded-full border bg-card px-3 py-1 text-xs font-medium text-brand-strong">
              <Sparkles className="size-3.5" aria-hidden /> Humanización visual con IA local
            </p>
            <h1 className="font-display text-5xl leading-[1.05] font-semibold tracking-tight text-balance md:text-6xl">
              Del retrato generado a una apariencia <span className="text-brand-strong italic">fotográfica</span>
            </h1>
            <p className="max-w-xl text-lg text-muted-foreground">
              Humaniza retratos sintéticos, restaura fotos deterioradas y prepara tus imágenes en un solo estudio.
              Compara cada cambio, conserva el original y trabaja con tu equipo.
            </p>
            <div className="flex flex-wrap gap-3">
              <Button size="lg" asChild className="h-12 rounded-full px-7 text-base">
                <Link to="/registro">Empezar gratis <ArrowRight className="size-4" aria-hidden /></Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="h-12 rounded-full px-7 text-base">
                <a href="#como-funciona">Ver cómo funciona</a>
              </Button>
            </div>
            <ul className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
              <li className="flex items-center gap-2"><Lock className="size-4 text-brand-strong" aria-hidden />Edición en el servidor local</li>
              <li className="flex items-center gap-2"><BadgeCheck className="size-4 text-brand-strong" aria-hidden />Original intacto</li>
              <li className="flex items-center gap-2"><ShieldCheck className="size-4 text-brand-strong" aria-hidden />Rotulado «editado con IA»</li>
            </ul>
          </div>
          <div className="mx-auto w-full max-w-md space-y-4">
            <BeforeAfterSlider before="/demo/retrato-generado.webp" after="/demo/retrato-humanizado.webp" beforeLabel="Generado con IA" afterLabel="Humanizado en LUMIA" />
            <p className="text-center text-xs leading-relaxed text-muted-foreground">Retrato fotográfico sintético de muestra. Izquierda: generado con IA. Derecha: el mismo archivo procesado por LUMIA. No es una fotografía de una persona real.</p>
          </div>
        </div>
      </section>

      <section id="herramientas" className="mx-auto max-w-6xl scroll-mt-24 px-4 py-20 md:px-6">
        <div className="max-w-2xl space-y-4"><p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-strong">Un estudio completo</p><h2 className="font-display text-4xl font-semibold tracking-tight">De la primera foto a tu entrega final</h2><p className="text-muted-foreground">Herramientas para editar, organizar y colaborar. La edición local funciona sin saldo de API externa.</p></div>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            ["01", "Humanización local", "Retratos sintéticos con microtextura y realce de reflejos existentes en los ojos. Comparación y descarga rotulada."],
            ["02", "Restauración de fotos", "Reduce ruido y recupera tonos. Marca rayas o manchas pequeñas para repararlas sin sobrescribir el original."],
            ["03", "Estudio de edición", "Quitar lunares, cambiar o quitar fondo, desenfoque gaussiano, nitidez, resolución, luz, color y rotación."],
            ["04", "Asistente de edición", "Una guía de objetivos y pasos concretos que abre la herramienta indicada. Sin llamadas a servicios de chat."],
            ["05", "Galería y álbumes", "Carga varias imágenes, organiza tus archivos y guarda resultados para continuar editándolos."],
            ["06", "Trabajos en segundo plano", "Sigue utilizando la web mientras se procesa una imagen. Recupera el resultado desde el historial."],
            ["07", "Equipos e invitaciones", "Invita por enlace, prepara un correo o compártelo por WhatsApp. Cada persona crea su propia contraseña."],
            ["08", "Tu espacio, tu estilo", "Avatares de iniciales o iconos, cuatro acentos, tema claro/oscuro/sistema y navegación compacta en este navegador."],
            ["09", "Horario y seguimiento", "Configura tu horario, registra entrada y salida, consulta horas y exporta el resumen del equipo a CSV."],
          ].map(([number, title, description]) => <article key={number} className="space-y-3 rounded-3xl border bg-card p-6 shadow-sm"><span className="text-xs font-semibold tracking-widest text-brand-strong">{number}</span><h3 className="text-lg font-semibold">{title}</h3><p className="text-sm leading-relaxed text-muted-foreground">{description}</p></article>)}
        </div>
        <p className="mt-6 text-xs text-muted-foreground">Integración opcional: generación de imágenes con Gemini, disponible cuando el proyecto de Google tenga cuota. No se incluye como servicio activo sin validar esa cuota.</p>
      </section>

      {/* ---------- El problema ---------- */}
      <section className="border-y bg-secondary/50">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-20 md:px-6 lg:grid-cols-[1fr_1.4fr]">
          <div className="space-y-4">
            <p className="text-xs font-semibold tracking-[0.18em] text-brand-strong uppercase">El problema</p>
            <h2 className="font-display text-4xl font-semibold tracking-tight text-balance">Los retratos sintéticos delatan su origen</h2>
            <p className="text-muted-foreground">
              Quien crea imágenes con IA suele regenerar muchas veces o retocar a mano para que un rostro no se vea artificial.
              LUMIA AI reduce ese trabajo con una sola edición controlada.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            {SINTOMAS.map((s, i) => (
              <div key={s.t} className="rounded-3xl border bg-card p-6 shadow-sm">
                <p className="font-display text-3xl text-brand">0{i + 1}</p>
                <p className="mt-3 font-semibold">{s.t}</p>
                <p className="mt-1 text-sm text-muted-foreground">{s.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------- Qué mejora ---------- */}
      <section id="que-mejora" className="mx-auto max-w-6xl scroll-mt-24 px-4 py-24 md:px-6">
        <div className="mx-auto max-w-2xl space-y-4 text-center">
          <p className="text-xs font-semibold tracking-[0.18em] text-brand-strong uppercase">Qué mejora</p>
          <h2 className="font-display text-4xl font-semibold tracking-tight text-balance">Cuatro detalles que hacen creíble un rostro</h2>
          <p className="text-muted-foreground">Acercamientos del resultado de muestra procesado por LUMIA. El comparador superior conserva el original para revisar las diferencias reales.</p>
        </div>
        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {MEJORAS.map(({ kind, icon: Icon, t, d }) => (
            <article key={t} className="flex flex-col gap-4 rounded-3xl border bg-card p-5 shadow-sm">
              <img src="/demo/retrato-humanizado.webp" alt={`Detalle del retrato de muestra: ${t}`} loading="lazy" className="h-40 w-full rounded-2xl object-cover" style={{ objectPosition: ({ piel: "50% 50%", ojos: "50% 34%", cabello: "20% 20%", luz: "50% 60%" })[kind] }} />
              <div className="flex items-center gap-2">
                <span className="grid size-8 place-items-center rounded-xl bg-brand-soft text-brand-strong"><Icon className="size-4" aria-hidden /></span>
                <h3 className="font-semibold">{t}</h3>
              </div>
              <p className="text-sm text-muted-foreground">{d}</p>
            </article>
          ))}
        </div>
      </section>

      {/* ---------- Cómo funciona ---------- */}
      <section id="como-funciona" className="scroll-mt-24 bg-primary text-primary-foreground">
        <div className="mx-auto max-w-6xl px-4 py-24 md:px-6">
          <div className="max-w-2xl space-y-4">
            <p className="text-xs font-semibold tracking-[0.18em] text-[oklch(0.85_0.08_65)] uppercase">Cómo funciona</p>
            <h2 className="font-display text-4xl font-semibold tracking-tight text-balance">De tu archivo a la comparación, en cuatro pasos</h2>
          </div>
          <ol className="mt-14 grid gap-6 md:grid-cols-4">
            {PASOS.map(({ icon: Icon, t, d }, i) => (
              <li key={t} className="relative rounded-3xl bg-white/[0.06] p-6 ring-1 ring-white/10">
                <span className="absolute top-6 right-6 font-display text-4xl text-white/15">{i + 1}</span>
                <span className="grid size-11 place-items-center rounded-2xl bg-[oklch(0.6_0.11_48)] text-white"><Icon className="size-5" aria-hidden /></span>
                <p className="mt-6 font-semibold">{t}</p>
                <p className="mt-2 text-sm text-primary-foreground/75">{d}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* ---------- Privacidad y límites ---------- */}
      <section id="privacidad" className="mx-auto grid max-w-6xl scroll-mt-24 gap-8 px-4 py-24 md:px-6 lg:grid-cols-2">
        <div className="rounded-3xl border bg-card p-8 shadow-sm">
          <span className="grid size-11 place-items-center rounded-2xl bg-brand-soft text-brand-strong"><Lock className="size-5" aria-hidden /></span>
          <h2 className="mt-6 font-display text-3xl font-semibold">Privacidad por diseño</h2>
          <ul className="mt-6 space-y-3 text-sm text-muted-foreground">
            <li className="flex gap-3"><BadgeCheck className="mt-0.5 size-4 shrink-0 text-emerald-700" aria-hidden />Solo tú ves tus imágenes, salvo que compartas una con tu equipo.</li>
            <li className="flex gap-3"><BadgeCheck className="mt-0.5 size-4 shrink-0 text-emerald-700" aria-hidden />La edición ocurre en la computadora que aloja la aplicación. Gemini recibe solo tu descripción, con consentimiento.</li>
            <li className="flex gap-3"><BadgeCheck className="mt-0.5 size-4 shrink-0 text-emerald-700" aria-hidden />El administrador técnico ve métricas agregadas, nunca tus fotos.</li>
            <li className="flex gap-3"><BadgeCheck className="mt-0.5 size-4 shrink-0 text-emerald-700" aria-hidden />Los resultados conservan los metadatos de procedencia y se rotulan.</li>
          </ul>
        </div>
        <div className="rounded-3xl border bg-secondary/50 p-8">
          <span className="grid size-11 place-items-center rounded-2xl bg-card text-foreground"><ShieldCheck className="size-5" aria-hidden /></span>
          <h2 className="mt-6 font-display text-3xl font-semibold">Lo que LUMIA AI no hace</h2>
          <ul className="mt-6 space-y-3 text-sm text-muted-foreground">
            <li className="flex gap-3"><X className="mt-0.5 size-4 shrink-0 text-red-700" aria-hidden />No convierte una imagen sintética en la foto de una persona real.</li>
            <li className="flex gap-3"><X className="mt-0.5 size-4 shrink-0 text-red-700" aria-hidden />No borra metadatos de procedencia ni oculta que hubo edición con IA.</li>
            <li className="flex gap-3"><X className="mt-0.5 size-4 shrink-0 text-red-700" aria-hidden />No ofrece suplantación de identidad ni cambia el rostro de nadie.</li>
            <li className="flex gap-3"><X className="mt-0.5 size-4 shrink-0 text-red-700" aria-hidden />No garantiza reparar manos ni anatomía.</li>
          </ul>
        </div>
      </section>

      {/* ---------- Para equipos ---------- */}
      <section className="border-y bg-secondary/40">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-20 md:px-6 lg:grid-cols-3">
          {[
            { icon: Users, t: "Equipos con invitación", d: "Un enlace de un solo uso que vence en 72 horas." },
            { icon: FileCheck2, t: "Compartir con intención", d: "Solo se comparte lo que tú eliges, imagen por imagen." },
            { icon: MonitorSmartphone, t: "En escritorio y celular", d: "La interfaz se adapta a la pantalla y se maneja con teclado." },
          ].map(({ icon: Icon, t, d }) => (
            <div key={t} className="flex gap-4">
              <span className="grid size-11 shrink-0 place-items-center rounded-2xl bg-card text-brand-strong shadow-sm"><Icon className="size-5" aria-hidden /></span>
              <div><p className="font-semibold">{t}</p><p className="mt-1 text-sm text-muted-foreground">{d}</p></div>
            </div>
          ))}
        </div>
      </section>

      {/* ---------- Preguntas ---------- */}
      <section id="preguntas" className="mx-auto max-w-3xl scroll-mt-24 px-4 py-24 md:px-6">
        <h2 className="text-center font-display text-4xl font-semibold tracking-tight">Preguntas frecuentes</h2>
        <div className="mt-10 divide-y rounded-3xl border bg-card">
          {FAQ.map((f) => (
            <details key={f.q} className="group p-6 [&_summary::-webkit-details-marker]:hidden">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-medium">
                {f.q}<span className="text-xl text-muted-foreground transition group-open:rotate-45" aria-hidden>+</span>
              </summary>
              <p className="mt-3 text-sm text-muted-foreground">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* ---------- Llamado final ---------- */}
      <section className="px-4 pb-24 md:px-6">
        <div className="relative mx-auto max-w-6xl overflow-hidden rounded-[2rem] bg-primary px-8 py-16 text-center text-primary-foreground">
          <div aria-hidden className="absolute -top-24 left-1/2 size-[30rem] -translate-x-1/2 rounded-full bg-[oklch(0.6_0.11_48/0.35)] blur-3xl" />
          <h2 className="relative font-display text-4xl font-semibold tracking-tight text-balance">Prueba LUMIA AI con tu primer retrato</h2>
          <p className="relative mx-auto mt-4 max-w-xl text-primary-foreground/80">Crea tu cuenta, sube una imagen generada por IA y compara el resultado en minutos.</p>
          <Button size="lg" variant="secondary" asChild className="relative mt-8 h-12 rounded-full px-8 text-base">
            <Link to="/registro">Crear mi cuenta</Link>
          </Button>
        </div>
      </section>
    </>
  );
}
