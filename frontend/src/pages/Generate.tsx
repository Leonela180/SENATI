import { useState } from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, CloudUpload, ImagePlus, Loader2, Sparkles, Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/PageHeader";
import { useAlbums } from "@/features/gallery/useGallery";
import { useGenerate, useGenerationStatus, useGenerations } from "@/features/generations/useGenerations";
import { fecha } from "@/components/JobCard";

const IDEAS = [
  "Retrato fotográfico de una mujer joven en un café, luz natural de ventana, fondo desenfocado",
  "Retrato de un hombre adulto en una oficina moderna, iluminación suave de estudio",
  "Persona mayor sonriendo en un parque al atardecer, estilo fotografía documental",
];

export default function Generate() {
  const { data: status } = useGenerationStatus();
  const { data: history } = useGenerations();
  const { data: albums } = useAlbums();
  const gen = useGenerate();
  const [prompt, setPrompt] = useState("");
  const [consent, setConsent] = useState(false);
  const [albumId, setAlbumId] = useState<number | null>(null);
  const result = gen.data;

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Generar" title="Generar imágenes con IA"
                  description="Describe la imagen que necesitas. Se genera con Gemini de Google y se guarda en tu galería, lista para editar o humanizar." />

      {status && !status.configured && (
        <div role="status" className="flex gap-3 rounded-2xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
          <AlertTriangle className="size-5 shrink-0" aria-hidden />
          <p><strong>Falta configurar Gemini.</strong> Agrega tu clave en el archivo <code>.env</code> con la línea <code>GEMINI_API_KEY=tu_clave</code> y reinicia LUMIA AI. La clave nunca se sube a GitHub.</p>
        </div>
      )}

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <section className="space-y-5 rounded-3xl border bg-card p-6 shadow-sm">
          <div className="space-y-2">
            <Label htmlFor="prompt">Descripción</Label>
            <textarea id="prompt" value={prompt} onChange={(e) => setPrompt(e.target.value)} maxLength={1000} rows={5}
                      placeholder="Ej.: retrato fotográfico de una persona en un estudio, luz suave…"
                      className="w-full resize-y rounded-xl border bg-background p-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring" />
            <p className="text-right text-xs text-muted-foreground">{prompt.length}/1000</p>
          </div>
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Ideas para empezar</p>
            <div className="flex flex-wrap gap-2">
              {IDEAS.map((i) => <button key={i} onClick={() => setPrompt(i)} className="rounded-full border px-3 py-1 text-left text-xs hover:bg-muted">{i.slice(0, 48)}…</button>)}
            </div>
          </div>
          <label className="block space-y-1 text-sm">
            <span className="font-medium">Guardar en</span>
            <select value={albumId ?? ""} onChange={(e) => setAlbumId(e.target.value ? Number(e.target.value) : null)} className="w-full rounded-xl border bg-background px-3 py-2">
              <option value="">Galería (sin álbum)</option>
              {albums?.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
          </label>
          <div className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50/60 p-4">
            <Checkbox id="consent" checked={consent} onCheckedChange={(v) => setConsent(v === true)} className="mt-0.5" />
            <Label htmlFor="consent" className="text-sm font-normal leading-snug">
              <span className="flex items-center gap-1 font-medium"><CloudUpload className="size-4" aria-hidden />Servicio externo</span>
              Entiendo que la descripción se envía a Google (Gemini) para generar la imagen. Es la única función de LUMIA AI que usa internet.
            </Label>
          </div>
          {gen.error && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{(gen.error as Error).message}</p>}
          <Button size="lg" className="h-12 w-full rounded-xl text-base" disabled={!consent || prompt.trim().length < 5 || gen.isPending || status?.configured === false}
                  onClick={() => gen.mutate({ prompt: prompt.trim(), albumId })}>
            {gen.isPending ? <><Loader2 className="size-4 animate-spin" aria-hidden />Generando… (puede tardar unos segundos)</> : <><Sparkles className="size-4" aria-hidden />Generar imagen</>}
          </Button>
        </section>

        <section className="space-y-4">
          {result?.image ? (
            <div className="space-y-4">
              <img src={`/api/v1/images/${result.image.id}/content`} alt={`Imagen generada: ${result.prompt}`} className="mx-auto max-h-[60vh] rounded-3xl shadow-xl ring-1 ring-black/5" />
              <p className="text-center text-xs text-muted-foreground">Generada con {result.model} en {result.seconds} s · guardada en tu galería</p>
              <div className="flex flex-wrap justify-center gap-3">
                <Button asChild className="rounded-full"><Link to={`/app/estudio?image=${result.image.id}`}><Wand2 className="size-4" aria-hidden />Editar en el Estudio</Link></Button>
                <Button asChild variant="outline" className="rounded-full"><Link to={`/app/humanizar?image=${result.image.id}`}><Sparkles className="size-4" aria-hidden />Humanizar</Link></Button>
              </div>
            </div>
          ) : (
            <div className="flex h-full min-h-80 flex-col items-center justify-center gap-3 rounded-3xl border border-dashed p-8 text-center text-muted-foreground">
              {gen.isPending ? <Loader2 className="size-8 animate-spin" aria-hidden /> : <ImagePlus className="size-8" aria-hidden />}
              <p>{gen.isPending ? "Gemini está creando tu imagen…" : "Aquí aparecerá la imagen generada."}</p>
            </div>
          )}
        </section>
      </div>

      {!!history?.length && (
        <section className="space-y-4">
          <h2 className="font-display text-2xl font-semibold">Generaciones recientes</h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
            {history.map((h) => (
              <figure key={h.id} className="overflow-hidden rounded-2xl border bg-card">
                {h.image_id ? (
                  <Link to={`/app/estudio?image=${h.image_id}`}><img src={`/api/v1/images/${h.image_id}/content`} alt="" loading="lazy" className="aspect-square w-full object-cover" /></Link>
                ) : <div className="grid aspect-square place-items-center bg-muted p-2 text-center text-xs text-muted-foreground">{h.status === "failed" ? `Error: ${h.error_code}` : "Imagen borrada"}</div>}
                <figcaption className="space-y-0.5 p-2"><p className="line-clamp-2 text-xs" title={h.prompt}>{h.prompt}</p><p className="text-[10px] text-muted-foreground">{fecha(h.created_at)}</p></figcaption>
              </figure>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
