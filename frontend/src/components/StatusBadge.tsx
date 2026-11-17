import { cn } from "@/lib/utils";
import type { JobStatus } from "@/lib/types";

const LABEL: Record<JobStatus, string> = { queued: "En cola", processing: "Procesando", completed: "Completado", failed: "Error" };
const STYLE: Record<JobStatus, string> = {
  queued: "bg-secondary text-secondary-foreground",
  processing: "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  completed: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  failed: "bg-red-500/15 text-red-700 dark:text-red-300",
};
const DOT: Record<JobStatus, string> = {
  queued: "bg-stone-400", processing: "bg-amber-500 pulse-dot", completed: "bg-emerald-600", failed: "bg-red-600",
};

export function StatusBadge({ status, className }: { status: JobStatus; className?: string }) {
  return (
    <span className={cn("inline-flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium", STYLE[status], className)}>
      <span className={cn("size-1.5 rounded-full", DOT[status])} aria-hidden />
      {LABEL[status]}
    </span>
  );
}
