import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { Crop, Droplets, Eraser, Fingerprint, ImagePlus, Palette, RotateCcw, RotateCw, SlidersHorizontal, Sparkles, Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/PageHeader";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";
import { ProcessingView } from "@/components/ProcessingView";
import { ImageDropzone } from "@/components/ImageDropzone";
import { useImage, useImages, useSaveResult, useUploadToGallery } from "@/features/gallery/useGallery";
import { useCreateJob } from "@/features/jobs/useJobs";
import { cn } from "@/lib/utils";
import type { Job, Tool } from "@/lib/types";

type EditTool = Exclude<Tool, "humanizar">;
const TOOLS: { id: EditTool; label: string; icon: typeof Eraser; help: string }[] = [
  { id: "textura_piel", label: "Textura de piel", icon: Fingerprint, help: "Quita el aspecto «de plástico»: agrega poros, grano fino y pequeños brillos solo en la piel. Ojos, boca, cejas y lunares no se tocan." },
  { id: "restaurar", label: "Restaurar foto", icon: RotateCcw, help: "Recupera tonos y contraste y reduce ruido. Marca rayas o manchas pequeñas para repararlas. No reconstruye rostros ni colorea fotos en blanco y negro." },
  { id: "quitar_lunar", label: "Quitar lunar", icon: Eraser, help: "Haz clic sobre cada lunar o mancha. Se rellena con la piel de alrededor." },
  { id: "cambiar_fondo", label: "Cambiar fondo", icon: Palette, help: "La IA recorta a la persona y cambia el fondo por un color, un desenfoque o transparencia." },
  { id: "desenfoque", label: "Desenfoque", icon: Droplets, help: "Desenfoque gaussiano de toda la imagen o solo del fondo (efecto retrato)." },
  { id: "mejorar_calidad", label: "Mejorar calidad", icon: Wand2, help: "Reduce el ruido, duplica la resolución y mejora la nitidez." },
  { id: "ajustes", label: "Ajustes", icon: SlidersHorizontal, help: "Brillo, contraste, saturación, calidez y rotación." },
];

function Slider({ label, value, min, max, step, onChange, fmt }: { label: string; value: number; min: number; max: number; step: number; onChange: (v: number) => void; fmt?: (v: number) => string }) {
  return (
    <label className="block space-y-1.5 text-sm">
      <span className="flex justify-between"><span className="font-medium">{label}</span><span className="text-muted-foreground">{fmt ? fmt(value) : value}</span></span>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} className="w-full accent-[var(--g2)]" />
    </label>
  );
}

export default function Studio() {
  const [params, setParams] = useSearchParams();
  const imageId = Number(params.get("image")) || null;
  const { data: image } = useImage(imageId);
  const { data: recent } = useImages("", "", 1);
  const upload = useUploadToGallery();
  const createJob = useCreateJob();
  const saveResult = useSaveResult();
  const [declared, setDeclared] = useState(false);
  const [tool, setTool] = useState<EditTool>(() => TOOLS.some(t => t.id === params.get("tool")) ? params.get("tool") as EditTool : "restaurar");
  const [intensity, setIntensity] = useState(0.6);
  const [points, setPoints] = useState<{ x: number; y: number; r: number }[]>([]);
  const [brush, setBrush] = useState(12);
  const [bg, setBg] = useState({ mode: "color", color: "#f4efe8", radius: 14 });
  const [blur, setBlur] = useState({ radius: 6, scope: "fondo" });
  const [quality, setQuality] = useState({ scale: 2, sharpen: 0.6, denoise: true });
  const [adj, setAdj] = useState({ brightness: 1, contrast: 1, saturation: 1, warmth: 0, rotate: 0 });
  const [skin, setSkin] = useState({ intensity: 0.7, pecas: false });
  const [jobId, setJobId] = useState<number | null>(null);
  const [done, setDone] = useState<Job | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => { setPoints([]); setJobId(null); setDone(null); }, [imageId, tool]);
  const src = imageId ? `/api/v1/images/${imageId}/content` : "";
  const toolInfo = TOOLS.find((t) => t.id === tool)!;

  // Vista previa aproximada en el navegador (el resultado final lo calcula el servidor)
  const previewFilter = useMemo(() => {
    if (tool === "ajustes") return `brightness(${adj.brightness}) contrast(${adj.contrast}) saturate(${adj.saturation}) sepia(${Math.max(0, adj.warmth) * 0.25})`;
    if (tool === "desenfoque" && blur.scope === "todo") return `blur(${blur.radius / 2}px)`;
    return undefined;
  }, [tool, adj, blur]);

  function addPoint(e: React.MouseEvent<HTMLImageElement>) {
    if (!["quitar_lunar", "restaurar"].includes(tool) || !image || !imgRef.current || points.length >= 20) return;
    const rect = imgRef.current.getBoundingClientRect();
    const k = image.width / rect.width;
    setPoints([...points, {
      x: Math.max(0, Math.min(image.width - 1, Math.round((e.clientX - rect.left) * k))),
      y: Math.max(0, Math.min(image.height - 1, Math.round((e.clientY - rect.top) * k))),
      r: Math.max(2, Math.min(80, Math.round(brush * k))),
    }]);
  }

  function toolParams(): Record<string, unknown> {
    switch (tool) {
      case "textura_piel": return skin;
      case "restaurar": return { points, intensity };
      case "quitar_lunar": return { points };
      case "cambiar_fondo": return bg;
      case "desenfoque": return blur;
      case "mejorar_calidad": return quality;
      default: return adj;
    }
  }

  function apply() {
    if (!imageId) return;
    createJob.mutate({ image_id: imageId, preset: "natural", key: crypto.randomUUID(), tool, params: toolParams() },
      { onSuccess: (j) => { setJobId(j.id); setDone(null); } });
  }

  function continueWithResult() {
    if (!done) return;
    saveResult.mutate(done.id, {
      onSuccess: (img) => { toast.success("Resultado guardado en tu galería. Puedes seguir editando."); setParams({ image: String(img.id) }); },
    });
  }

  // ---------- Sin imagen: elegir de la galería o subir ----------
  if (!imageId) {
    return (
      <div className="space-y-8">
        <PageHeader eyebrow="Estudio" title="Estudio de edición" description="Restaura fotos deterioradas, repara manchas, cambia el fondo y ajusta luz y color. Se procesa en la computadora que aloja LUMIA AI." />
        <div className="grid gap-8 lg:grid-cols-2">
          <section className="space-y-3">
            <h2 className="font-semibold">Subir una imagen nueva</h2>
            <ImageDropzone onPick={(f) => {
              if (!declared) { toast.error("Primero marca la confirmación."); return; }
              upload.mutate({ file: f }, { onSuccess: (img) => setParams({ image: String(img.id) }) });
            }} />
            <div className="flex items-start gap-3 rounded-2xl bg-muted p-4">
              <Checkbox id="decl-studio" checked={declared} onCheckedChange={(v) => setDeclared(v === true)} className="mt-0.5" />
              <Label htmlFor="decl-studio" className="text-sm font-normal leading-snug">Confirmo que tengo permiso para editar esta imagen y, si aparecen personas, su autorización.</Label>
            </div>
            {upload.error && <p role="alert" className="text-sm text-destructive">{(upload.error as Error).message}</p>}
          </section>
          <section className="space-y-3">
            <h2 className="font-semibold">O elige una de tu galería</h2>
            {recent?.items.length ? (
              <div className="grid grid-cols-3 gap-3">
                {recent.items.slice(0, 9).map((im) => (
                  <button key={im.id} onClick={() => setParams({ image: String(im.id) })} className="overflow-hidden rounded-2xl border bg-muted transition hover:ring-2 hover:ring-ring" aria-label={`Editar ${im.filename}`}>
                    <img src={`/api/v1/images/${im.id}/content`} alt="" className="aspect-square w-full object-cover" loading="lazy" />
                  </button>
                ))}
              </div>
            ) : <p className="rounded-2xl border border-dashed p-8 text-center text-sm text-muted-foreground">Tu galería está vacía.</p>}
            <Link to="/app/galeria" className="inline-block text-sm font-medium text-brand-strong hover:underline">Ir a la galería →</Link>
          </section>
        </div>
      </div>
    );
  }

  // ---------- Con imagen ----------
  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Estudio" title="Estudio de edición" description={image?.filename}
                  action={<Button variant="outline" className="rounded-full" onClick={() => setParams({})}><ImagePlus className="size-4" aria-hidden />Cambiar imagen</Button>} />

      <div className="flex gap-2 overflow-x-auto pb-1" role="tablist" aria-label="Herramientas">
        {TOOLS.map(({ id, label, icon: Icon }) => (
          <button key={id} role="tab" aria-selected={tool === id} onClick={() => setTool(id)}
                  className={cn("flex shrink-0 items-center gap-2 rounded-full border px-4 py-2 text-sm transition",
                    tool === id ? "border-primary bg-primary text-primary-foreground" : "bg-card hover:bg-muted")}>
            <Icon className="size-4" aria-hidden />{label}
          </button>
        ))}
      </div>

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_21rem]">
        <div>
          {done?.status === "completed" ? (
            <BeforeAfterSlider before={src} after={`/api/v1/jobs/${done.id}/download?inline=1`} />
          ) : jobId && !done ? (
            <ProcessingView jobId={jobId} preview={src} onDone={setDone} />
          ) : (
            <figure className="mx-auto w-fit max-w-full space-y-2">
              <div className="relative overflow-hidden rounded-3xl bg-muted shadow-xl ring-1 ring-black/5">
                <img ref={imgRef} src={src} alt="Imagen a editar" onClick={addPoint} draggable={false}
                     style={{ filter: previewFilter, transform: tool === "ajustes" && adj.rotate ? `rotate(${adj.rotate}deg)` : undefined }}
                     className={cn("block max-h-[68vh] w-auto max-w-full transition", ["quitar_lunar", "restaurar"].includes(tool) && "cursor-crosshair")} />
                {["quitar_lunar", "restaurar"].includes(tool) && image && imgRef.current && points.map((p, i) => {
                  const k = imgRef.current!.getBoundingClientRect().width / image.width;
                  return <span key={i} aria-hidden className="pointer-events-none absolute rounded-full border-2 border-white bg-white/25 shadow"
                               style={{ left: p.x * k - p.r * k, top: p.y * k - p.r * k, width: p.r * 2 * k, height: p.r * 2 * k }} />;
                })}
              </div>
              {previewFilter && <figcaption className="text-center text-xs text-muted-foreground">Vista previa aproximada; el resultado final lo calcula el servidor.</figcaption>}
            </figure>
          )}
          {done?.status === "failed" && <p role="alert" className="mt-4 rounded-xl bg-red-500/10 p-3 text-sm text-red-700 dark:text-red-300">{done.error_message}</p>}
        </div>

        <aside className="space-y-5 rounded-3xl border bg-card p-6 shadow-sm lg:self-start">
          <div>
            <p className="font-display text-xl font-semibold">{toolInfo.label}</p>
            <p className="mt-1 text-sm text-muted-foreground">{toolInfo.help}</p>
          </div>

          {tool === "restaurar" && <div className="space-y-3"><Slider label="Recuperación de tonos" value={intensity} min={0.1} max={1} step={0.1} onChange={setIntensity} fmt={v => `${Math.round(v * 100)} %`} /><p className="text-xs text-muted-foreground">Empieza suave. El original permanece intacto y cada resultado se guarda por separado.</p></div>}
          {["quitar_lunar", "restaurar"].includes(tool) && (
            <div className="space-y-4">
              <Slider label="Tamaño del pincel" value={brush} min={4} max={40} step={1} onChange={setBrush} fmt={(v) => `${v} px`} />
              <div className="flex items-center justify-between text-sm">
                <span>{points.length} {points.length === 1 ? "punto marcado" : "puntos marcados"}</span>
                <span className="flex gap-2">
                  <Button size="sm" variant="ghost" disabled={!points.length} onClick={() => setPoints(points.slice(0, -1))}>Deshacer</Button>
                  <Button size="sm" variant="ghost" disabled={!points.length} onClick={() => setPoints([])}>Limpiar</Button>
                </span>
              </div>
            </div>
          )}

          {tool === "textura_piel" && (
            <div className="space-y-4">
              <Slider label="Intensidad de la textura" value={skin.intensity} min={0.2} max={1} step={0.05} onChange={(v) => setSkin({ ...skin, intensity: v })} fmt={(v) => `${Math.round(v * 100)} %`} />
              <label className="flex items-center gap-2 text-sm"><Checkbox checked={skin.pecas} onCheckedChange={(v) => setSkin({ ...skin, pecas: v === true })} />Agregar pecas suaves</label>
              <p className="text-xs text-muted-foreground">Funciona con retratos donde la cara se ve de frente. Mira el resultado de cerca con el deslizador: los poros son finos, como en una foto real.</p>
            </div>
          )}

          {tool === "cambiar_fondo" && (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-2" role="radiogroup" aria-label="Tipo de fondo">
                {[["color", "Color"], ["desenfocado", "Desenfocado"], ["transparente", "Transparente"]].map(([v, l]) => (
                  <button key={v} role="radio" aria-checked={bg.mode === v} onClick={() => setBg({ ...bg, mode: v })}
                          className={cn("rounded-xl border px-2 py-2 text-xs", bg.mode === v ? "border-primary bg-secondary font-medium" : "hover:bg-muted")}>{l}</button>
                ))}
              </div>
              {bg.mode === "color" && (
                <div className="flex flex-wrap items-center gap-2">
                  {["#ffffff", "#f4efe8", "#d9e4f1", "#2f6fb0", "#1f1f1f"].map((c) => (
                    <button key={c} onClick={() => setBg({ ...bg, color: c })} aria-label={`Color ${c}`}
                            className={cn("size-8 rounded-full border-2", bg.color === c ? "border-primary" : "border-transparent ring-1 ring-black/10")} style={{ background: c }} />
                  ))}
                  <label className="flex items-center gap-2 text-xs text-muted-foreground">Otro
                    <input type="color" value={bg.color} onChange={(e) => setBg({ ...bg, color: e.target.value })} className="h-8 w-10 cursor-pointer rounded" />
                  </label>
                </div>
              )}
              {bg.mode === "desenfocado" && <Slider label="Intensidad" value={bg.radius} min={2} max={40} step={1} onChange={(v) => setBg({ ...bg, radius: v })} />}
            </div>
          )}

          {tool === "desenfoque" && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2" role="radiogroup" aria-label="Zona">
                {[["fondo", "Solo el fondo"], ["todo", "Toda la imagen"]].map(([v, l]) => (
                  <button key={v} role="radio" aria-checked={blur.scope === v} onClick={() => setBlur({ ...blur, scope: v })}
                          className={cn("rounded-xl border px-2 py-2 text-xs", blur.scope === v ? "border-primary bg-secondary font-medium" : "hover:bg-muted")}>{l}</button>
                ))}
              </div>
              <Slider label="Radio gaussiano" value={blur.radius} min={1} max={30} step={0.5} onChange={(v) => setBlur({ ...blur, radius: v })} />
            </div>
          )}

          {tool === "mejorar_calidad" && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2" role="radiogroup" aria-label="Escala">
                {[1, 2].map((s) => (
                  <button key={s} role="radio" aria-checked={quality.scale === s} onClick={() => setQuality({ ...quality, scale: s })}
                          className={cn("rounded-xl border px-2 py-2 text-xs", quality.scale === s ? "border-primary bg-secondary font-medium" : "hover:bg-muted")}>
                    {s === 1 ? "Mismo tamaño" : "Doble resolución"}
                  </button>
                ))}
              </div>
              <Slider label="Nitidez" value={quality.sharpen} min={0} max={2} step={0.1} onChange={(v) => setQuality({ ...quality, sharpen: v })} />
              <label className="flex items-center gap-2 text-sm"><Checkbox checked={quality.denoise} onCheckedChange={(v) => setQuality({ ...quality, denoise: v === true })} />Reducir ruido</label>
            </div>
          )}

          {tool === "ajustes" && (
            <div className="space-y-4">
              <Slider label="Brillo" value={adj.brightness} min={0.5} max={1.5} step={0.05} onChange={(v) => setAdj({ ...adj, brightness: v })} fmt={(v) => `${Math.round(v * 100)} %`} />
              <Slider label="Contraste" value={adj.contrast} min={0.5} max={1.5} step={0.05} onChange={(v) => setAdj({ ...adj, contrast: v })} fmt={(v) => `${Math.round(v * 100)} %`} />
              <Slider label="Saturación" value={adj.saturation} min={0} max={2} step={0.05} onChange={(v) => setAdj({ ...adj, saturation: v })} fmt={(v) => `${Math.round(v * 100)} %`} />
              <Slider label="Calidez" value={adj.warmth} min={-1} max={1} step={0.1} onChange={(v) => setAdj({ ...adj, warmth: v })} />
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-1"><Crop className="size-4" aria-hidden />Rotación: {adj.rotate}°</span>
                <span className="flex gap-1">
                  <Button size="icon" variant="outline" aria-label="Girar a la izquierda" onClick={() => setAdj({ ...adj, rotate: (adj.rotate + 270) % 360 })}><RotateCcw className="size-4" /></Button>
                  <Button size="icon" variant="outline" aria-label="Girar a la derecha" onClick={() => setAdj({ ...adj, rotate: (adj.rotate + 90) % 360 })}><RotateCw className="size-4" /></Button>
                </span>
              </div>
            </div>
          )}

          {createJob.error && <p role="alert" className="text-sm text-destructive">{(createJob.error as Error).message}</p>}

          {done?.status === "completed" ? (
            <div className="space-y-2">
              <Button asChild size="lg" className="h-11 w-full rounded-xl"><a href={`/api/v1/jobs/${done.id}/download`}>Descargar resultado</a></Button>
              <Button variant="outline" className="h-11 w-full rounded-xl" disabled={saveResult.isPending} onClick={continueWithResult}>Seguir editando este resultado</Button>
              <Button variant="ghost" className="w-full" onClick={() => { setJobId(null); setDone(null); }}>Probar otros ajustes</Button>
            </div>
          ) : (
            <Button size="lg" className="h-12 w-full rounded-xl text-base" onClick={apply}
                    disabled={createJob.isPending || (!!jobId && !done) || (tool === "quitar_lunar" && !points.length)}>
              <Sparkles className="size-4" aria-hidden />Aplicar
            </Button>
          )}
          <Link to={`/app/humanizar?image=${imageId}`} className="block text-center text-sm text-muted-foreground hover:text-foreground hover:underline">Humanizar esta imagen con IA →</Link>
        </aside>
      </div>
    </div>
  );
}
