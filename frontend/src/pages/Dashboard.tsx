import { Link } from "react-router-dom";
import { ArrowRight, CalendarClock, Cpu, History as HistoryIcon, Images, Sparkles, Users, Wand2, WandSparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmptyState, PageHeader, QueryError } from "@/components/PageHeader";
import { JobCard } from "@/components/JobCard";
import { StatusBadge } from "@/components/StatusBadge";
import { useMe } from "@/features/auth/useAuth";
import { useHealth, useJobs } from "@/features/jobs/useJobs";
import { useWorkspaces } from "@/features/teams/useTeams";
import { useHoursStatus, useHoursSummary } from "@/features/hours/useHours";

function Stat({ icon: Icon, label, children }: { icon: typeof Images; label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-4 rounded-3xl border bg-card p-5 shadow-sm">
      <span className="grid size-11 shrink-0 place-items-center rounded-2xl bg-brand-soft text-brand-strong"><Icon className="size-5" aria-hidden /></span>
      <div className="min-w-0"><p className="text-xs text-muted-foreground">{label}</p><div className="truncate text-lg font-semibold">{children}</div></div>
    </div>
  );
}

export default function Dashboard() {
  const { data: me } = useMe();
  const { data: health } = useHealth();
  const { data: jobs, isLoading: loadingJobs, isError: jobsError, isFetching, refetch } = useJobs(1);
  const { data: workspaces } = useWorkspaces();
  const team = workspaces?.find((w) => w.kind === "team");
  const last = jobs?.items[0];
  const firstName = me?.display_name.split(" ")[0] ?? "";
  const { data: hours } = useHoursSummary("week");
  const { data: clock } = useHoursStatus();
  const MODULES = [
    { to: "/app/humanizar", icon: Sparkles, title: "Humanizar", text: "Piel, ojos, cabello y luz más naturales con IA local." },
    { to: "/app/estudio", icon: Wand2, title: "Estudio de edición", text: "Quitar lunares, cambiar fondo, desenfoque y calidad." },
    { to: "/app/asistente", icon: WandSparkles, title: "Asistente de edición", text: "Encuentra un recorrido para restaurar y mejorar tus fotos." },
    { to: "/app/galeria", icon: Images, title: "Galería", text: "Sube, organiza en álbumes y procesa en lote." },
  ];

  return (
    <div className="space-y-10">
      <PageHeader eyebrow="Panel" title={`Hola, ${firstName}`}
                  description="Un espacio para crear, editar y organizar tus imágenes."
                  action={<Button variant="outline" asChild className="rounded-full px-6"><Link to="/app/galeria"><Images className="size-4" aria-hidden />Mi galería</Link></Button>} />

      <section className="relative overflow-hidden rounded-3xl border bg-secondary/60 p-6 md:p-9" aria-labelledby="crear-titulo">
        <div aria-hidden className="pointer-events-none absolute -right-16 -top-24 size-80 rounded-full bg-brand-soft/70 blur-3xl" />
        <div className="relative flex flex-wrap items-center justify-between gap-6">
          <div className="max-w-lg space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-strong">De la idea al detalle</p>
            <h2 id="crear-titulo" className="font-display text-3xl font-semibold leading-tight md:text-4xl">Dale forma a tu próxima imagen.</h2>
            <p className="text-sm leading-relaxed text-muted-foreground">Recupera una foto deteriorada o prepara un retrato con la guía del asistente. Tus originales se conservan para comparar cada cambio.</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button size="lg" asChild className="rounded-xl"><Link to="/app/asistente"><WandSparkles className="size-4" aria-hidden />Elegir mi recorrido</Link></Button>
            <Button size="lg" variant="outline" asChild className="rounded-xl bg-card"><Link to="/app/estudio"><Wand2 className="size-4" aria-hidden />Abrir Estudio</Link></Button>
          </div>
        </div>
      </section>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat icon={Images} label="Trabajos registrados">{jobs?.total ?? "—"}</Stat>
        <Stat icon={HistoryIcon} label="Último trabajo">{last ? <StatusBadge status={last.status} /> : "—"}</Stat>
        <Stat icon={Cpu} label="Motor de IA">{health ? (health.engine === "local" ? "IA local" : "Simulación") : "—"}</Stat>
        <Stat icon={Users} label="Equipo">{team?.name ?? "Sin equipo"}</Stat>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4" aria-label="Módulos">
        {MODULES.map(({ to, icon: Icon, title, text }) => (
          <Link key={to} to={to} className="group rounded-3xl border bg-card p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
            <span className="grid size-10 place-items-center rounded-2xl bg-primary text-primary-foreground"><Icon className="size-5" aria-hidden /></span>
            <p className="mt-4 font-semibold">{title}</p>
            <p className="mt-1 text-sm text-muted-foreground">{text}</p>
            <span className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-brand-strong">Abrir <ArrowRight className="size-4 transition group-hover:translate-x-0.5" aria-hidden /></span>
          </Link>
        ))}
      </section>

      <Link to="/app/horas" className="flex flex-wrap items-center gap-6 rounded-3xl border bg-card p-5 shadow-sm transition hover:shadow-md">
        <span className="grid size-11 place-items-center rounded-2xl bg-brand-soft text-brand-strong"><CalendarClock className="size-5" aria-hidden /></span>
        <div className="min-w-40"><p className="text-xs text-muted-foreground">Mi semana</p>
          <p className="font-semibold">{hours ? `${hours.worked} h trabajadas de ${hours.expected_to_date} h esperadas` : "—"}</p></div>
        <div className="min-w-32"><p className="text-xs text-muted-foreground">Por recuperar</p>
          <p className={hours && hours.to_recover > 0 ? "font-semibold text-red-700" : "font-semibold text-emerald-700"}>{hours ? (hours.to_recover > 0 ? `${hours.to_recover} h` : "Nada") : "—"}</p></div>
        <span className="ml-auto rounded-full bg-secondary px-3 py-1 text-sm">{clock?.open_entry ? "🟢 En jornada" : "Marcar entrada →"}</span>
      </Link>

      <section className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-2xl font-semibold">Trabajos recientes</h2>
          {!!jobs?.items.length && (
            <Link to="/app/historial" className="inline-flex items-center gap-1 text-sm font-medium text-brand-strong hover:underline">
              Ver historial <ArrowRight className="size-4" aria-hidden />
            </Link>
          )}
        </div>
        {jobsError ? <QueryError onRetry={() => { void refetch(); }} retrying={isFetching} /> : loadingJobs ? (
          <div role="status" aria-label="Cargando trabajos" className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => <div key={i} className="aspect-[4/5] animate-pulse rounded-2xl bg-muted" />)}
          </div>
        ) : jobs?.items.length ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {jobs.items.slice(0, 4).map((j) => <JobCard key={j.id} job={j} />)}
          </div>
        ) : (
          <EmptyState icon={<Sparkles className="size-6" />} title="Aún no tienes trabajos"
                      action={<Button asChild className="mt-2 rounded-full"><Link to="/app/humanizar">Subir mi primer retrato</Link></Button>}>
            Sube un retrato generado por IA y compara el antes y el después en esta misma pantalla.
          </EmptyState>
        )}
      </section>
    </div>
  );
}
