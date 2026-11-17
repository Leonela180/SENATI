import { Activity, Cpu, Database, Server, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/PageHeader";
import { useOverview, useResolveIncident } from "@/features/teams/useTeams";
import { cn } from "@/lib/utils";

function Health({ icon: Icon, label, ok, value }: { icon: typeof Server; label: string; ok: boolean; value: string }) {
  return (
    <div className="flex items-center gap-4 rounded-3xl border bg-card p-5 shadow-sm">
      <span className="grid size-11 place-items-center rounded-2xl bg-muted"><Icon className="size-5" aria-hidden /></span>
      <div className="min-w-0">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="flex items-center gap-2 font-semibold"><span className={cn("size-2 rounded-full", ok ? "bg-emerald-600" : "bg-red-600")} aria-hidden />{value}</p>
      </div>
    </div>
  );
}

export default function Admin() {
  const { data, error } = useOverview();
  const resolve = useResolveIncident();
  if (error) return <p role="alert" className="rounded-xl bg-red-500/10 p-4 text-red-700 dark:text-red-300">{(error as Error).message}</p>;
  if (!data) return <div className="h-96 animate-pulse rounded-3xl bg-muted" aria-label="Cargando" />;
  const j = data.jobs_by_status;
  const total = Math.max(1, j.queued + j.processing + j.completed + j.failed);
  const bars = [
    { k: "Completados", v: j.completed, c: "bg-emerald-600" }, { k: "En cola", v: j.queued, c: "bg-stone-400" },
    { k: "Procesando", v: j.processing, c: "bg-amber-500" }, { k: "Fallidos", v: j.failed, c: "bg-red-600" },
  ];

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Administración" title="Supervisión técnica" description="Solo métricas agregadas. Esta vista nunca muestra imágenes de los usuarios." />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Health icon={Server} label="API" ok={data.api === "ok"} value={data.api === "ok" ? "Operativa" : "Con errores"} />
        <Health icon={Database} label="Base de datos" ok={data.database === "ok"} value={data.database === "ok" ? "Conectada" : "Error"} />
        <Health icon={Activity} label="Worker" ok={data.worker.alive} value={data.worker.alive ? `Activo · ${data.worker.seconds_since_beat} s` : "Sin señal"} />
        <Health icon={Cpu} label="Motor" ok={data.engine === "local"} value={data.engine === "local" ? "IA local" : "Simulación"} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
        <section className="space-y-5 rounded-3xl border bg-card p-6 shadow-sm">
          <h2 className="font-semibold">Trabajos por estado</h2>
          <div className="flex h-3 overflow-hidden rounded-full bg-muted" aria-hidden>
            {bars.map((b) => <div key={b.k} className={b.c} style={{ width: `${(b.v / total) * 100}%` }} />)}
          </div>
          <dl className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {bars.map((b) => (
              <div key={b.k}><dt className="flex items-center gap-2 text-xs text-muted-foreground"><span className={cn("size-2 rounded-full", b.c)} aria-hidden />{b.k}</dt>
                <dd className="text-2xl font-semibold">{b.v}</dd></div>
            ))}
          </dl>
        </section>
        <section className="grid grid-cols-2 gap-4 rounded-3xl border bg-card p-6 shadow-sm">
          <div><p className="text-xs text-muted-foreground">Tiempo medio (24 h)</p><p className="text-2xl font-semibold">{data.avg_seconds_24h != null ? `${data.avg_seconds_24h} s` : "—"}</p></div>
          <div><p className="text-xs text-muted-foreground">Fallidos (24 h)</p><p className="text-2xl font-semibold">{data.failed_24h}</p></div>
          <div className="col-span-2 flex items-center gap-3 border-t pt-4"><Users className="size-5 text-brand-strong" aria-hidden />
            <p className="text-sm"><span className="text-2xl font-semibold">{data.users}</span> usuarios registrados</p></div>
        </section>
      </div>

      <section className="rounded-3xl border bg-card p-6 shadow-sm">
        <h2 className="font-semibold">Incidentes abiertos</h2>
        {data.open_incidents.length ? (
          <ul className="mt-4 divide-y">
            {data.open_incidents.map((i) => (
              <li key={i.id} className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
                <span><span className="font-medium">{i.service_name}</span> · <code className="rounded bg-muted px-1.5 py-0.5 text-xs">{i.error_code}</code>
                  <span className="block text-xs text-muted-foreground">{new Date(i.occurred_at).toLocaleString("es-PE")}</span></span>
                <Button size="sm" variant="outline" className="rounded-full" onClick={() => resolve.mutate(i.id)}>Marcar resuelto</Button>
              </li>
            ))}
          </ul>
        ) : <p className="mt-3 text-sm text-muted-foreground">Sin incidentes abiertos. Todo funciona con normalidad.</p>}
      </section>
    </div>
  );
}
