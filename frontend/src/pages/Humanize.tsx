import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { AlertTriangle, Download, Fingerprint, RotateCcw, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/PageHeader";
import { ImageDropzone } from "@/components/ImageDropzone";
import { ProcessingView } from "@/components/ProcessingView";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";
import { presetLabel } from "@/components/JobCard";
import { useUploadImage } from "@/features/images/useImages";
import { useCreateJob, useHealth } from "@/features/jobs/useJobs";
import { useImage, useSaveResult } from "@/features/gallery/useGallery";
import { cn } from "@/lib/utils";
import type { ImageInfo, Job } from "@/lib/types";

const PASOS = ["Imagen", "Procesamiento", "Resultado"];
const PRESET_HINT: Record<string, string> = {
  natural: "Equilibrado, recomendado",
  fotografico: "Un poco más de textura",
  detalle_suave: "El cambio más sutil",
};

function Stepper({ step }: { step: number }) {
  return (
    <ol className="flex items-center gap-3 text-sm" aria-label="Pasos">
      {PASOS.map((p, i) => (
        <li key={p} className="flex items-center gap-3" aria-current={i === step ? "step" : undefined}>
          <span className={cn("grid size-7 place-items-center rounded-full text-xs font-semibold",
            i < step ? "bg-emerald-600 text-white" : i === step ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground")}>{i + 1}</span>
          <span className={cn(i === step ? "font-medium" : "text-muted-foreground", "hidden sm:inline")}>{p}</span>
          {i < PASOS.length - 1 && <span className="h-px w-8 bg-border md:w-16" aria-hidden />}
        </li>
      ))}
    </ol>
  );
}

export default function Humanize() {
  const { data: health } = useHealth();
  const upload = useUploadImage();
  const createJob = useCreateJob();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const navigate = useNavigate();
  const saveResult = useSaveResult();
  const [declared, setDeclared] = useState(false);
  const [preset, setPreset] = useState("natural");
  const [image, setImage] = useState<ImageInfo | null>(null);   // ya subida: no se vuelve a subir al reintentar
  const [key, setKey] = useState("");                            // una clave de idempotencia por intención (RF-09)
  const [jobId, setJobId] = useState<number | null>(null);
  const [done, setDone] = useState<Job | null>(null);
  const presets = health?.presets ?? [];

  useEffect(() => () => { if (preview.startsWith("blob:")) URL.revokeObjectURL(preview); }, [preview]);
  // Desde la galería o el Estudio: /app/humanizar?image=ID (la imagen ya está subida y declarada)
  const [params] = useSearchParams();
  const fromGallery = Number(params.get("image")) || null;
  const { data: galleryImage } = useImage(fromGallery);
  useEffect(() => {
    if (galleryImage && !image) {
      setImage(galleryImage); setPreview(`/api/v1/images/${galleryImage.id}/content`); setDeclared(true);
      setFile(new File([], galleryImage.filename));
    }
  }, [galleryImage]); // eslint-disable-line react-hooks/exhaustive-deps

  const step = done?.status === "completed" ? 2 : jobId ? 1 : 0;
  const busy = upload.isPending || createJob.isPending;
  const error = (upload.error as Error | null)?.message || (createJob.error as Error | null)?.message;

  function choose(f: File) {
    setFile(f); setImage(null); setKey("");
    setPreview(URL.createObjectURL(f));
  }

  async function humanize() {
    if (!file) return;
    const k = key || crypto.randomUUID();
    setKey(k);
    const img = image ?? await upload.mutateAsync(file).catch(() => null);
    if (!img) return;
    setImage(img);
    createJob.mutate({ image_id: img.id, preset, key: k }, { onSuccess: (j) => { setJobId(j.id); setDone(null); } });
  }

  function reset() {
    setFile(null); setPreview(""); setDeclared(false); setImage(null); setKey(""); setJobId(null); setDone(null);
    upload.reset(); createJob.reset();
  }

  function retry() { setKey(""); setDone(null); setJobId(null); createJob.reset(); }

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Estudio" title="Humanizar un retrato" description="Sube un retrato generado por IA. El original se conserva y el resultado se rotula como editado con IA."
                  action={<Stepper step={step} />} />

      {/* ---------- Paso 1: elegir y confirmar ---------- */}
      {step === 0 && !jobId && (
        !file ? <ImageDropzone onPick={choose} /> : (
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem]">
            <div className="relative mx-auto w-fit max-w-full overflow-hidden rounded-3xl bg-muted shadow-xl ring-1 ring-black/5">
              <img src={preview} alt="Vista previa de la imagen seleccionada" className="block max-h-[65vh] w-auto max-w-full" />
            </div>
            <aside className="space-y-6 rounded-3xl border bg-card p-6 shadow-sm lg:self-start">
              <div>
                <p className="truncate font-medium" title={file.name}>{file.name}</p>
                <p className="text-sm text-muted-foreground">{image && !file.size ? "Desde tu galería" : file.size < 1024 * 1024 ? `${Math.max(1, Math.round(file.size / 1024))} KB` : `${(file.size / 1024 / 1024).toFixed(1)} MB`} ·{" "}
                  <button className="font-medium text-brand-strong underline-offset-4 hover:underline" onClick={reset}>Cambiar imagen</button></p>
              </div>

              {presets.length > 1 && (
                <fieldset className="space-y-2">
                  <legend className="mb-2 text-sm font-medium">Intensidad</legend>
                  {presets.map((p) => (
                    <label key={p} className={cn("flex cursor-pointer items-center justify-between rounded-2xl border px-4 py-3 text-sm transition",
                      preset === p ? "border-primary bg-secondary" : "hover:bg-muted")}>
                      <span><span className="font-medium">{presetLabel(p)}</span><span className="block text-xs text-muted-foreground">{PRESET_HINT[p]}</span></span>
                      <input type="radio" name="preset" value={p} checked={preset === p} onChange={() => { setPreset(p); setKey(""); }} className="accent-[var(--g2)]" />
                    </label>
                  ))}
                </fieldset>
              )}

              <div className="flex items-start gap-3 rounded-2xl bg-muted p-4">
                <Checkbox id="declaracion" checked={declared} onCheckedChange={(v) => setDeclared(v === true)} className="mt-0.5" />
                <Label htmlFor="declaracion" className="text-sm leading-snug font-normal">
                  Confirmo que la imagen es generada por IA y que tengo permiso para usarla
                </Label>
              </div>

              {error && <p role="alert" className="rounded-xl bg-red-500/10 p-3 text-sm text-red-700 dark:text-red-300">{error}</p>}
              <Button size="lg" className="h-12 w-full rounded-xl text-base" disabled={!declared || busy} onClick={humanize}>
                <Sparkles className="size-4" aria-hidden />{busy ? "Enviando…" : "Humanizar imagen"}
              </Button>
              {!declared && <p className="text-center text-xs text-muted-foreground">Marca la confirmación para continuar.</p>}
            </aside>
          </div>
        )
      )}

      {/* ---------- Paso 2: procesamiento ---------- */}
      {jobId && done?.status !== "completed" && (
        done?.status === "failed" ? (
          <div className="mx-auto max-w-lg space-y-4 rounded-3xl border border-red-500/30 bg-red-500/10 p-8 text-center" role="alert">
            <AlertTriangle className="mx-auto size-8 text-red-700 dark:text-red-300" aria-hidden />
            <p className="font-display text-2xl font-semibold text-red-700 dark:text-red-300">No se pudo procesar la imagen</p>
            <p className="text-sm text-red-700 dark:text-red-300">{done.error_message ?? "Ocurrió un error en el motor."}</p>
            <div className="flex justify-center gap-3">
              <Button onClick={retry} className="rounded-full"><RotateCcw className="size-4" aria-hidden />Reintentar</Button>
              <Button variant="outline" onClick={reset} className="rounded-full">Usar otra imagen</Button>
            </div>
          </div>
        ) : <ProcessingView jobId={jobId} preview={preview} onDone={setDone} />
      )}

      {/* ---------- Paso 3: resultado ---------- */}
      {done?.status === "completed" && (
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_20rem]">
          <BeforeAfterSlider before={`/api/v1/images/${done.image_id}/content`} after={`/api/v1/jobs/${done.id}/download?inline=1`} />
          <aside className="space-y-5 rounded-3xl border bg-card p-6 shadow-sm lg:self-start">
            <div>
              <p className="font-display text-2xl font-semibold">Tu resultado está listo</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {done.model_id === "mock" ? "Simulación, sin IA real." : `Intensidad ${presetLabel(done.preset).toLowerCase()}.`} El archivo se descarga rotulado «editado con IA».
              </p>
            </div>
            <Button size="lg" asChild className="h-12 w-full rounded-xl text-base">
              <a href={`/api/v1/jobs/${done.id}/download`}><Download className="size-4" aria-hidden />Descargar resultado</a>
            </Button>
            {done.parameters.facial_detail_applied === true && (
              <p className="text-sm text-muted-foreground">Microtextura de piel ajustada conservando los rasgos.
                {Number(done.parameters.eyes_enhanced) > 0 && " Reflejos existentes en los ojos realzados."}
              </p>
            )}
            {done.parameters.facial_detail_applied === false && (
              <p className="text-sm text-muted-foreground">No se detectó un rostro frontal con suficiente confianza para ajustar poros y reflejos. Se conserva la edición base de IA.</p>
            )}
            <Button variant="outline" className="h-11 w-full rounded-xl" disabled={saveResult.isPending}
                    onClick={() => saveResult.mutate(done.id, { onSuccess: (img) => navigate(`/app/estudio?image=${img.id}&tool=textura_piel`) })}>
              <Fingerprint className="size-4" aria-hidden />Agregar textura de piel
            </Button>
            <Button variant="ghost" className="h-11 w-full rounded-xl" onClick={reset}>Humanizar otra imagen</Button>
            <Link to={`/app/trabajos/${done.id}`} className="block text-center text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline">
              Ver detalle y trazabilidad
            </Link>
          </aside>
        </div>
      )}
    </div>
  );
}
