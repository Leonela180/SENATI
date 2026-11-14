import { Link } from "react-router-dom";
import { ImageIcon } from "lucide-react";
import { StatusBadge } from "@/components/StatusBadge";
import type { Job } from "@/lib/types";

const PRESET: Record<string, string> = { natural: "Natural", fotografico: "Fotográfico", detalle_suave: "Detalle suave" };

export const presetLabel = (p: string) => PRESET[p] ?? p;
export const fecha = (iso: string) =>
  new Date(iso).toLocaleString("es-PE", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });

/** Miniatura: el resultado si está completado (vista en línea, no cuenta como descarga) o el original. */
export function JobThumb({ job, className = "" }: { job: Job; className?: string }) {
  const src = job.status === "completed" ? `/api/v1/jobs/${job.id}/download?inline=1` : `/api/v1/images/${job.image_id}/content`;
  return (
    <div className={`relative overflow-hidden bg-muted ${className}`}>
      <ImageIcon className="absolute inset-0 m-auto size-6 text-muted-foreground/40" aria-hidden />
      <img src={src} alt="" loading="lazy" className="relative h-full w-full object-cover" onError={(e) => { e.currentTarget.style.display = "none"; }} />
    </div>
  );
}

export function JobCard({ job }: { job: Job }) {
  return (
    <Link to={`/app/trabajos/${job.id}`}
          className="group block overflow-hidden rounded-2xl border bg-card shadow-sm transition hover:-translate-y-0.5 hover:shadow-md focus-visible:ring-2 focus-visible:ring-ring">
      <JobThumb job={job} className="aspect-[4/5]" />
      <div className="space-y-2 p-4">
        <div className="flex items-center justify-between gap-2">
          <p className="truncate text-sm font-medium" title={job.image_filename}>{job.image_filename}</p>
          <StatusBadge status={job.status} />
        </div>
        <p className="text-xs text-muted-foreground">{job.tool === "humanizar" ? `Humanización ${presetLabel(job.preset).toLowerCase()}` : job.tool_label} · {fecha(job.created_at)}</p>
      </div>
    </Link>
  );
}
