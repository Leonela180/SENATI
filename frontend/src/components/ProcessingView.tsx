import { useEffect, useState } from "react";
import { Check, Loader2 } from "lucide-react";
import { useJob } from "@/features/jobs/useJobs";
import { cn } from "@/lib/utils";
import type { Job } from "@/lib/types";

/** Vista de procesamiento: la imagen con un barrido suave y la línea de tiempo del trabajo (RF-11). */
export function ProcessingView({ jobId, preview, onDone }: { jobId: number; preview?: string; onDone?: (j: Job) => void }) {
  const { data } = useJob(jobId);
  const [seconds, setSeconds] = useState(0);
  const status = data?.status ?? "queued";

  useEffect(() => {
    const t = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);
  useEffect(() => {
    if (data && (data.status === "completed" || data.status === "failed")) onDone?.(data);
  }, [data?.status]); // eslint-disable-line react-hooks/exhaustive-deps

  const steps = [
    { key: "upload", label: "Imagen recibida", done: true, active: false },
    { key: "queued", label: "En cola", done: status !== "queued", active: status === "queued" },
    { key: "processing", label: "Humanizando en tu PC", done: status === "completed" || status === "failed", active: status === "processing" },
    { key: "done", label: "Listo para comparar", done: status === "completed", active: false },
  ];

  return (
    <div className="grid items-center gap-8 md:grid-cols-[minmax(0,1fr)_minmax(0,18rem)]" aria-live="polite">
      <div className="relative mx-auto w-fit max-w-full overflow-hidden rounded-3xl bg-muted shadow-xl ring-1 ring-black/5">
        {preview ? <img src={preview} alt="Imagen en proceso" className="block max-h-[60vh] w-auto max-w-full opacity-90" />
                 : <div className="aspect-[4/5] w-72" />}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="scan-line h-1/3 w-full bg-gradient-to-b from-transparent via-white/35 to-transparent" />
        </div>
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-4 text-sm text-white">
          {status === "processing" ? "Ajustando piel, ojos, cabello y luz…" : "Esperando turno en la cola…"}
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <p className="font-display text-2xl font-semibold">Procesando tu imagen</p>
          <p className="text-sm text-muted-foreground">Tiempo transcurrido: {seconds} s{data && data.attempt_count > 1 ? ` · intento ${data.attempt_count}` : ""}</p>
        </div>
        <ol className="space-y-4">
          {steps.map((s) => (
            <li key={s.key} className="flex items-center gap-3">
              <span className={cn("grid size-7 shrink-0 place-items-center rounded-full border text-xs",
                s.done ? "border-emerald-600 bg-emerald-600 text-white" : s.active ? "border-brand text-brand-strong" : "text-muted-foreground")}>
                {s.done ? <Check className="size-4" aria-hidden /> : s.active ? <Loader2 className="size-4 animate-spin" aria-hidden /> : null}
              </span>
              <span className={cn("text-sm", s.active ? "font-medium" : !s.done && "text-muted-foreground")}>{s.label}</span>
            </li>
          ))}
        </ol>
        <p className="rounded-2xl bg-muted p-3 text-xs text-muted-foreground">
          Puedes salir de esta pantalla: el trabajo sigue en tu historial y te mostrará el resultado al terminar.
        </p>
      </div>
    </div>
  );
}
