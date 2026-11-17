import type { ReactNode } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export function QueryError({ onRetry, retrying = false }: { onRetry: () => void; retrying?: boolean }) {
  return (
    <div role="alert" className="flex flex-wrap items-center gap-4 rounded-2xl border border-destructive/25 bg-card p-5">
      <AlertCircle className="size-5 shrink-0 text-destructive" aria-hidden />
      <div className="min-w-0 flex-1">
        <p className="font-medium">No pudimos cargar esta información</p>
        <p className="mt-1 text-sm text-muted-foreground">Comprueba tu conexión e inténtalo de nuevo.</p>
      </div>
      <Button variant="outline" onClick={onRetry} disabled={retrying}>
        <RefreshCw className={retrying ? "size-4 animate-spin" : "size-4"} aria-hidden />
        {retrying ? "Reintentando…" : "Reintentar"}
      </Button>
    </div>
  );
}

export function PageHeader({ title, description, action, eyebrow }: { title: ReactNode; description?: ReactNode; action?: ReactNode; eyebrow?: string }) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4 border-b pb-6">
      <div className="space-y-1.5">
        {eyebrow && <p className="text-xs font-semibold tracking-[0.18em] text-brand-strong uppercase">{eyebrow}</p>}
        <h1 className="font-display text-3xl font-semibold tracking-tight md:text-4xl">{title}</h1>
        {description && <p className="max-w-2xl text-muted-foreground">{description}</p>}
      </div>
      {action}
    </header>
  );
}

export function EmptyState({ icon, title, children, action }: { icon: ReactNode; title: string; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-3xl border border-dashed bg-card/60 px-6 py-14 text-center">
      <div className="grid size-12 place-items-center rounded-2xl bg-brand-soft text-brand-strong">{icon}</div>
      <h2 className="font-display text-xl font-semibold">{title}</h2>
      {children && <p className="max-w-md text-sm text-muted-foreground">{children}</p>}
      {action}
    </div>
  );
}
