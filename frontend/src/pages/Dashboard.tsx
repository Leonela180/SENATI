import { Link } from "react-router-dom";
import { ArrowRight, Cpu, History as HistoryIcon, Images, Sparkles, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmptyState, PageHeader } from "@/components/PageHeader";
import { JobCard } from "@/components/JobCard";
import { StatusBadge } from "@/components/StatusBadge";
import { useMe } from "@/features/auth/useAuth";
import { useHealth, useJobs } from "@/features/jobs/useJobs";
import { useWorkspaces } from "@/features/teams/useTeams";

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
  const { data: jobs } = useJobs(1);
  const { data: workspaces } = useWorkspaces();
  const team = workspaces?.find((w) => w.kind === "team");
  const last = jobs?.items[0];
  const firstName = me?.display_name.split(" ")[0] ?? "";

  return (
    <div className="space-y-10">
      <PageHeader eyebrow="Panel" title={`Hola, ${firstName}`}
                  description="Aquí ves tus últimos trabajos y el estado del motor."
                  action={<Button size="lg" asChild className="rounded-full px-6"><Link to="/app/humanizar"><Sparkles className="size-4" aria-hidden />Humanizar una imagen</Link></Button>} />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat icon={Images} label="Trabajos realizados">{jobs?.total ?? 0}</Stat>
        <Stat icon={HistoryIcon} label="Último trabajo">{last ? <StatusBadge status={last.status} /> : "—"}</Stat>
        <Stat icon={Cpu} label="Motor de IA">{health ? (health.engine === "local" ? "Local (GPU)" : "Simulación") : "—"}</Stat>
        <Stat icon={Users} label="Equipo">{team?.name ?? "Sin equipo"}</Stat>
      </div>

      <section className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-2xl font-semibold">Trabajos recientes</h2>
          {!!jobs?.items.length && (
            <Link to="/app/historial" className="inline-flex items-center gap-1 text-sm font-medium text-brand-strong hover:underline">
              Ver historial <ArrowRight className="size-4" aria-hidden />
            </Link>
          )}
        </div>
        {jobs?.items.length ? (
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
