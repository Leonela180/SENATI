import { useState } from "react";
import { Link } from "react-router-dom";
import { ChevronLeft, ChevronRight, History as HistoryIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmptyState, PageHeader } from "@/components/PageHeader";
import { JobCard } from "@/components/JobCard";
import { useJobs } from "@/features/jobs/useJobs";
import { useWorkspaces } from "@/features/teams/useTeams";
import { cn } from "@/lib/utils";

export default function History() {
  const [page, setPage] = useState(1);
  const [ws, setWs] = useState<number | undefined>(undefined);
  const { data: workspaces } = useWorkspaces();
  const team = workspaces?.find((w) => w.kind === "team");
  const { data, isLoading } = useJobs(page, ws);
  const tabs = [{ id: undefined, label: "Mis trabajos" }, ...(team ? [{ id: team.id, label: `Compartidos en ${team.name}` }] : [])];

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Historial" title="Tus trabajos"
                  description={data ? `${data.total} ${data.total === 1 ? "trabajo" : "trabajos"} en total.` : undefined}
                  action={tabs.length > 1 && (
                    <div className="inline-flex rounded-full border bg-card p-1" role="tablist" aria-label="Ver trabajos">
                      {tabs.map((t) => (
                        <button key={t.label} role="tab" aria-selected={ws === t.id}
                                onClick={() => { setPage(1); setWs(t.id); }}
                                className={cn("rounded-full px-4 py-1.5 text-sm transition", ws === t.id ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground")}>
                          {t.label}
                        </button>
                      ))}
                    </div>
                  )} />

      {isLoading ? (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="aspect-[4/5] animate-pulse rounded-2xl bg-muted" />)}
        </div>
      ) : data?.items.length ? (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {data.items.map((j) => <JobCard key={j.id} job={j} />)}
        </div>
      ) : (
        <EmptyState icon={<HistoryIcon className="size-6" />} title={ws ? "Tu equipo aún no comparte imágenes" : "No hay trabajos todavía"}
                    action={!ws && <Button asChild className="mt-2 rounded-full"><Link to="/app/humanizar">Humanizar una imagen</Link></Button>}>
          {ws ? "Cuando alguien comparta una imagen con el equipo, aparecerá aquí." : "Tus imágenes procesadas aparecerán aquí."}
        </EmptyState>
      )}

      {data && data.pages > 1 && (
        <nav className="flex items-center justify-center gap-3" aria-label="Paginación">
          <Button variant="outline" size="icon" className="rounded-full" disabled={page <= 1} onClick={() => setPage(page - 1)} aria-label="Página anterior"><ChevronLeft className="size-4" /></Button>
          <span className="text-sm text-muted-foreground">Página {data.page} de {data.pages}</span>
          <Button variant="outline" size="icon" className="rounded-full" disabled={page >= data.pages} onClick={() => setPage(page + 1)} aria-label="Página siguiente"><ChevronRight className="size-4" /></Button>
        </nav>
      )}
    </div>
  );
}
