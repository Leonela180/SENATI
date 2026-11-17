import { Link, useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { AlertTriangle, ArrowLeft, Download, RotateCcw, Share2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";
import { ProcessingView } from "@/components/ProcessingView";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState, QueryError } from "@/components/PageHeader";
import { ApiError } from "@/lib/api";
import { fecha, presetLabel } from "@/components/JobCard";
import { useCreateJob, useJob } from "@/features/jobs/useJobs";
import { useSetVisibility } from "@/features/images/useImages";
import { useWorkspaces } from "@/features/teams/useTeams";

const PARAM_LABEL: Record<string, string> = {
  strength: "Fuerza", steps: "Pasos", guidance: "Guía", seed: "Semilla",
  work_size: "Tamaño de trabajo (px)", seconds: "Tiempo (s)", vram_gb: "VRAM máx. (GB)",
};

export default function JobDetail() {
  const id = Number(useParams().id);
  const nav = useNavigate();
  const { data: job, isError, error, isFetching, refetch } = useJob(id);
  const retry = useCreateJob();
  const share = useSetVisibility();
  const { data: workspaces } = useWorkspaces();
  const inTeam = workspaces?.some((w) => w.kind === "team");

  if (isError && !(error instanceof ApiError && error.status === 404)) return <div className="space-y-3"><p className="text-sm text-muted-foreground">No se pudo consultar el estado. El trabajo continúa en el servidor; este aviso no indica que haya fallado.</p><QueryError onRetry={() => { void refetch(); }} retrying={isFetching} /></div>;
  if (isError) return (
    <EmptyState icon={<AlertTriangle className="size-6" />} title="No encontrado"
                action={<Button asChild variant="outline" className="mt-2 rounded-full"><Link to="/app/historial">Volver al historial</Link></Button>}>
      Este trabajo no existe o no tienes permiso para verlo.
    </EmptyState>
  );
  if (!job) return <div className="h-96 animate-pulse rounded-3xl bg-muted" aria-label="Cargando" />;

  const active = job.status === "queued" || job.status === "processing";
  const rows: [string, string][] = [
    ["Estado", job.status_label], ["Creado", fecha(job.created_at)],
    ["Intensidad", presetLabel(job.preset)], ["Modelo", job.model_id ?? "—"], ["Versión", job.model_version ?? "—"],
    ["Intentos", String(job.attempt_count)],
    ...Object.entries(job.parameters).map(([k, v]) => [PARAM_LABEL[k] ?? k, Array.isArray(v) ? v.join(" × ") : String(v)] as [string, string]),
  ];

  return (
    <div className="space-y-8">
      <div className="space-y-4 border-b pb-6">
        <Link to="/app/historial" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="size-4" aria-hidden />Historial
        </Link>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="min-w-0 truncate font-display text-3xl font-semibold tracking-tight md:text-4xl">{job.image_filename}</h1>
          <StatusBadge status={job.status} />
          {job.model_id === "mock" && <span className="rounded-full bg-amber-500/15 px-2.5 py-0.5 text-xs text-amber-700 dark:text-amber-300">Simulación, sin IA real</span>}
        </div>
      </div>

      {active ? <ProcessingView jobId={job.id} preview={`/api/v1/images/${job.image_id}/content`} /> : (
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_20rem]">
          {job.status === "completed" ? (
            <BeforeAfterSlider before={`/api/v1/images/${job.image_id}/content`} after={`/api/v1/jobs/${job.id}/download?inline=1`} />
          ) : (
            <div className="space-y-3 rounded-3xl border border-red-500/30 bg-red-500/10 p-8" role="alert">
              <AlertTriangle className="size-7 text-red-700 dark:text-red-300" aria-hidden />
              <p className="font-display text-2xl font-semibold text-red-700 dark:text-red-300">El procesamiento falló</p>
              <p className="text-sm text-red-700 dark:text-red-300">{job.error_message}</p>
            </div>
          )}

          <aside className="space-y-4 lg:self-start">
            <div className="space-y-3 rounded-3xl border bg-card p-5 shadow-sm">
              {job.status === "completed" && (
                <Button asChild size="lg" className="h-11 w-full rounded-xl"><a href={`/api/v1/jobs/${job.id}/download`}><Download className="size-4" aria-hidden />Descargar resultado</a></Button>
              )}
              {job.is_owner && (
                <Button variant="outline" className="h-11 w-full rounded-xl" disabled={retry.isPending}
                        onClick={() => retry.mutate({ image_id: job.image_id, preset: job.preset, key: crypto.randomUUID() },
                                                    { onSuccess: (j) => nav(`/app/trabajos/${j.id}`) })}>
                  <RotateCcw className="size-4" aria-hidden />{job.status === "failed" ? "Reintentar" : "Procesar de nuevo"}
                </Button>
              )}
              {job.is_owner && inTeam && (
                <Button variant="ghost" className="h-11 w-full rounded-xl" disabled={share.isPending}
                        onClick={() => share.mutate({ imageId: job.image_id, visibility: job.visibility === "team" ? "private" : "team" },
                                                    { onSuccess: () => toast.success(job.visibility === "team" ? "Ahora es privada" : "Compartida con tu equipo") })}>
                  <Share2 className="size-4" aria-hidden />{job.visibility === "team" ? "Dejar de compartir" : "Compartir con mi equipo"}
                </Button>
              )}
            </div>
            <details className="group rounded-3xl border bg-card p-5 shadow-sm" open>
              <summary className="cursor-pointer list-none font-medium [&::-webkit-details-marker]:hidden">
                Trazabilidad <span className="text-xs font-normal text-muted-foreground">(RNF-10)</span>
              </summary>
              <dl className="mt-4 space-y-2 text-sm">
                {rows.map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-4 border-b border-dashed pb-2 last:border-0">
                    <dt className="text-muted-foreground">{k}</dt><dd className="truncate text-right font-medium" title={v}>{v}</dd>
                  </div>
                ))}
              </dl>
            </details>
          </aside>
        </div>
      )}
    </div>
  );
}
