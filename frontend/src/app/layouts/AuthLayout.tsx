import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, Sparkles, Undo2 } from "lucide-react";
import { Logo } from "@/components/brand/Logo";

const POINTS = [
  { icon: Sparkles, text: "Piel, ojos, cabello y luz más fotográficos, sin cambiar a la persona." },
  { icon: ShieldCheck, text: "Tus imágenes se procesan en esta computadora y solo tú las ves." },
  { icon: Undo2, text: "El original nunca se modifica: siempre puedes comparar." },
];

/** Pantallas de ingreso: panel de marca a la izquierda y formulario a la derecha. */
export function AuthLayout({ title, subtitle, children, footer }: { title: string; subtitle: string; children: ReactNode; footer: ReactNode }) {
  return (
    <div className="grid min-h-screen bg-background font-sans text-foreground lg:grid-cols-2">
      <aside className="relative hidden overflow-hidden bg-secondary text-foreground lg:flex lg:flex-col lg:justify-between lg:p-12">
        <div aria-hidden className="aurora absolute inset-0" />
        <div aria-hidden className="grid-lines absolute inset-0 opacity-60" />
        <Logo className="relative" />
        <div className="relative space-y-8">
          <p className="font-display text-4xl leading-tight font-semibold text-balance">
            Retratos generados por IA que se ven <span className="text-gradient">reales</span>.
          </p>
          <ul className="space-y-4">
            {POINTS.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-start gap-3 text-sm text-muted-foreground">
                <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-card text-brand-strong shadow-sm"><Icon className="size-4" aria-hidden /></span>
                <span className="pt-1.5">{text}</span>
              </li>
            ))}
          </ul>
        </div>
        <p className="relative text-xs text-muted-foreground">Procesamiento local · Resultados rotulados «editado con IA»</p>
      </aside>

      <main className="flex flex-col px-4 py-8 md:px-10">
        <div className="flex items-center justify-between">
          <span className="lg:invisible"><Logo /></span>
          <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">← Volver al inicio</Link>
        </div>
        <div className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center py-10">
          <h1 className="font-display text-3xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-2 mb-8 text-muted-foreground">{subtitle}</p>
          {children}
          <div className="mt-8 text-center text-sm text-muted-foreground">{footer}</div>
        </div>
      </main>
    </div>
  );
}
