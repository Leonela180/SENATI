import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { CheckSquare, ChevronLeft, ChevronRight, Folder, FolderPlus, Images, Layers, Search, Trash2, Upload, Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { EmptyState, PageHeader, QueryError } from "@/components/PageHeader";
import { useAlbums, useCreateAlbum, useDeleteAlbum, useDeleteImage, useImages, useMoveImage, useUploadToGallery } from "@/features/gallery/useGallery";
import { useCreateJob } from "@/features/jobs/useJobs";
import { cn } from "@/lib/utils";
import type { Tool } from "@/lib/types";

const BATCH: { tool: Tool; label: string; params: Record<string, unknown> }[] = [
  { tool: "mejorar_calidad", label: "Mejorar calidad (×2)", params: { scale: 2, sharpen: 0.6, denoise: true } },
  { tool: "desenfoque", label: "Desenfocar el fondo", params: { radius: 8, scope: "fondo" } },
  { tool: "cambiar_fondo", label: "Fondo blanco", params: { mode: "color", color: "#ffffff" } },
  { tool: "ajustes", label: "Más luz y color (+10 %)", params: { brightness: 1.1, contrast: 1.05, saturation: 1.1, warmth: 0, rotate: 0 } },
  { tool: "humanizar", label: "Humanizar con IA", params: {} },
];

export default function Gallery() {
  const [album, setAlbum] = useState("");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<number[]>([]);
  const [declared, setDeclared] = useState(false);
  const [newAlbum, setNewAlbum] = useState("");
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null);
  const [batchBusy, setBatchBusy] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const { data: albums } = useAlbums();
  const { data, isLoading, isError, isFetching, refetch } = useImages(album, q, page);
  const uploadImg = useUploadToGallery();
  const createAlbum = useCreateAlbum();
  const deleteAlbum = useDeleteAlbum();
  const move = useMoveImage();
  const del = useDeleteImage();
  const createJob = useCreateJob();
  const currentAlbum = albums?.find((a) => String(a.id) === album);

  async function uploadMany(files: FileList | null) {
    if (!files?.length) return;
    if (!declared) { toast.error("Marca la confirmación de que las imágenes son generadas por IA."); return; }
    const list = Array.from(files).slice(0, 20);
    if (files.length > 20) toast.info("Se subirán las primeras 20 imágenes. Puedes subir las demás después.");
    setProgress({ done: 0, total: list.length });
    let ok = 0;
    for (const [i, f] of list.entries()) {
      try { await uploadImg.mutateAsync({ file: f, albumId: currentAlbum?.id ?? null }); ok++; }
      catch (e) { toast.error(`${f.name}: ${(e as Error).message}`); }
      setProgress({ done: i + 1, total: list.length });
    }
    setProgress(null);
    if (ok) toast.success(`${ok} ${ok === 1 ? "imagen subida" : "imágenes subidas"}`);
    if (fileRef.current) fileRef.current.value = "";
  }

  async function runBatch(idx: number) {
    if (batchBusy) return;
    setBatchBusy(true);
    const b = BATCH[idx];
    let ok = 0;
    const failed: number[] = [];
    for (const id of selected) {
      try { await createJob.mutateAsync({ image_id: id, preset: "natural", key: crypto.randomUUID(), tool: b.tool, params: b.params }); ok++; }
      catch (e) { failed.push(id); toast.error((e as Error).message); }
    }
    if (ok) toast.success(`${ok} trabajos de «${b.label}» en cola. Míralos en el historial.`);
    setSelected(failed);
    setBatchBusy(false);
  }

  async function deleteSelected() {
    if (batchBusy) return;
    if (!window.confirm(`¿Borrar ${selected.length} ${selected.length === 1 ? "imagen" : "imágenes"} y sus resultados? No se puede deshacer.`)) return;
    setBatchBusy(true);
    const failed: number[] = [];
    for (const id of selected) {
      try { await del.mutateAsync(id); }
      catch (e) { failed.push(id); toast.error((e as Error).message); }
    }
    if (selected.length > failed.length) toast.success(`${selected.length - failed.length} imágenes borradas.`);
    setSelected(failed);
    setBatchBusy(false);
  }

  async function moveSelected(value: string) {
    if (batchBusy || !value) return;
    setBatchBusy(true);
    const failed: number[] = [];
    for (const id of selected) {
      try { await move.mutateAsync({ id, albumId: value === "none" ? null : Number(value) }); }
      catch (e) { failed.push(id); toast.error((e as Error).message); }
    }
    if (selected.length > failed.length) toast.success("Imágenes movidas al álbum.");
    setSelected(failed);
    setBatchBusy(false);
  }

  const toggle = (id: number) => { if (!batchBusy) setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id])); };
  const albumBtn = (value: string, label: string, count?: number) => (
    <button key={value} onClick={() => { setAlbum(value); setPage(1); setSelected([]); }}
            className={cn("flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-sm transition",
              album === value ? "bg-primary text-primary-foreground" : "hover:bg-muted")}>
      <span className="flex min-w-0 items-center gap-2"><Folder className="size-4 shrink-0" aria-hidden /><span className="truncate">{label}</span></span>
      {count !== undefined && <span className="text-xs opacity-70">{count}</span>}
    </button>
  );

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Galería" title="Tus imágenes" description="Sube varias imágenes a la vez, organízalas en álbumes y aplica herramientas en lote."
                  action={
                    <Button className="rounded-full" onClick={() => fileRef.current?.click()} disabled={!!progress}>
                      <Upload className="size-4" aria-hidden />{progress ? `Subiendo ${progress.done}/${progress.total}…` : "Subir imágenes"}
                    </Button>
                  } />
      <input ref={fileRef} type="file" multiple accept="image/jpeg,image/png,image/webp" className="sr-only" aria-label="Seleccionar imágenes"
             onChange={(e) => uploadMany(e.target.files)} />

      <div className="grid gap-8 lg:grid-cols-[15rem_minmax(0,1fr)]">
        <aside className="space-y-5">
          <div className="flex items-start gap-3 rounded-2xl bg-muted p-3">
            <Checkbox id="decl-gal" checked={declared} onCheckedChange={(v) => setDeclared(v === true)} className="mt-0.5" />
            <Label htmlFor="decl-gal" className="text-xs font-normal leading-snug">Confirmo que las imágenes que subo son generadas por IA y tengo permiso para usarlas</Label>
          </div>
          <nav className="space-y-1" aria-label="Álbumes">
            {albumBtn("", "Todas")}
            {albumBtn("none", "Sin álbum")}
            {albums?.map((a) => albumBtn(String(a.id), a.name, a.count))}
          </nav>
          <form className="flex gap-2" onSubmit={(e) => { e.preventDefault(); if (newAlbum.trim()) createAlbum.mutate(newAlbum.trim(), { onSuccess: () => setNewAlbum("") }); }}>
            <Input value={newAlbum} onChange={(e) => setNewAlbum(e.target.value)} placeholder="Nuevo álbum" aria-label="Nombre del nuevo álbum" maxLength={80} />
            <Button type="submit" size="icon" variant="outline" aria-label="Crear álbum"><FolderPlus className="size-4" /></Button>
          </form>
          {createAlbum.error && <p className="text-xs text-destructive">{(createAlbum.error as Error).message}</p>}
          {currentAlbum && (
            <Button variant="ghost" size="sm" className="text-muted-foreground"
                    onClick={() => { if (window.confirm("¿Borrar el álbum? Las imágenes se conservan.")) deleteAlbum.mutate(currentAlbum.id, { onSuccess: () => setAlbum("") }); }}>
              <Trash2 className="size-4" aria-hidden />Borrar álbum
            </Button>
          )}
        </aside>

        <section className="space-y-5">
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative min-w-56 flex-1">
              <Search className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden />
              <Input value={q} onChange={(e) => { setQ(e.target.value); setPage(1); setSelected([]); }} placeholder="Buscar por nombre" className="pl-9" aria-label="Buscar imágenes" disabled={batchBusy} />
            </div>
            {data && <span className="text-sm text-muted-foreground">{data.total} {data.total === 1 ? "imagen" : "imágenes"}</span>}
          </div>

          {selected.length > 0 && (
            <fieldset disabled={batchBusy} aria-busy={batchBusy} className="flex min-w-0 flex-wrap items-center gap-2 rounded-2xl border bg-secondary/60 p-3">
              <span className="flex items-center gap-2 text-sm font-medium"><CheckSquare className="size-4" aria-hidden />{selected.length} seleccionadas</span>
              <span className="mx-1 h-5 w-px bg-border" aria-hidden />
              <Layers className="size-4 text-muted-foreground" aria-hidden />
              {BATCH.map((b, i) => (
                <Button key={b.tool} size="sm" variant="outline" className="rounded-full bg-card" disabled={createJob.isPending} onClick={() => runBatch(i)}>{b.label}</Button>
              ))}
              <select aria-label="Mover a álbum" className="rounded-full border bg-card px-3 py-1.5 text-sm" value=""
                      onChange={(e) => { void moveSelected(e.target.value); }}>
                <option value="" disabled>Mover a…</option>
                <option value="none">Sin álbum</option>
                {albums?.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
              </select>
              <Button size="sm" variant="ghost" className="text-red-700" onClick={deleteSelected}><Trash2 className="size-4" aria-hidden />Borrar</Button>
              <Button size="sm" variant="ghost" onClick={() => setSelected([])}>Cancelar</Button>
            </fieldset>
          )}

          {isError ? <QueryError onRetry={() => { void refetch(); }} retrying={isFetching} /> : isLoading ? (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
              {Array.from({ length: 8 }).map((_, i) => <div key={i} className="aspect-square animate-pulse rounded-2xl bg-muted" />)}
            </div>
          ) : data?.items.length ? (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
              {data.items.map((im) => {
                const isSel = selected.includes(im.id);
                return (
                  <figure key={im.id} className={cn("group relative overflow-hidden rounded-2xl border bg-card shadow-sm transition", isSel && "ring-2 ring-primary")}>
                    <button onClick={() => toggle(im.id)} className="block w-full" aria-pressed={isSel} aria-label={`Seleccionar ${im.filename}`}>
                      <img src={im.last_job_id ? `/api/v1/jobs/${im.last_job_id}/download?inline=1` : `/api/v1/images/${im.id}/content`}
                           alt="" loading="lazy" className="aspect-square w-full bg-muted object-cover" />
                    </button>
                    <span className={cn("absolute top-2 left-2 grid size-6 place-items-center rounded-md border-2 border-white bg-black/30 text-xs text-white transition",
                      isSel ? "bg-primary" : "opacity-0 group-hover:opacity-100")} aria-hidden>{isSel ? "✓" : ""}</span>
                    {im.last_job_id && <span className="absolute top-2 right-2 rounded-full bg-white/90 px-2 py-0.5 text-[10px] font-medium">Editada</span>}
                    <figcaption className="flex items-center justify-between gap-2 p-3">
                      <span className="truncate text-xs" title={im.filename}>{im.filename}</span>
                      <span className="flex shrink-0 gap-1">
                        <Link to={`/app/estudio?image=${im.id}`} className="rounded-lg p-1.5 hover:bg-muted" aria-label="Editar en el Estudio" title="Editar en el Estudio"><Wand2 className="size-4" /></Link>
                        <button onClick={() => { if (window.confirm("¿Borrar esta imagen y sus resultados?")) del.mutate(im.id); }} className="rounded-lg p-1.5 text-red-700 hover:bg-red-50" aria-label="Borrar" title="Borrar"><Trash2 className="size-4" /></button>
                      </span>
                    </figcaption>
                  </figure>
                );
              })}
            </div>
          ) : (
            <EmptyState icon={<Images className="size-6" />} title={q ? "Sin resultados" : "No hay imágenes aquí"}
                        action={<Button className="mt-2 rounded-full" onClick={() => fileRef.current?.click()}><Upload className="size-4" aria-hidden />Subir imágenes</Button>}>
              Sube imágenes generadas por IA o créalas en «Generar con IA».
            </EmptyState>
          )}

          {data && data.pages > 1 && (
            <nav className="flex items-center justify-center gap-3" aria-label="Paginación">
              <Button variant="outline" size="icon" className="rounded-full" disabled={page <= 1} onClick={() => setPage(page - 1)} aria-label="Página anterior"><ChevronLeft className="size-4" /></Button>
              <span className="text-sm text-muted-foreground">Página {data.page} de {data.pages}</span>
              <Button variant="outline" size="icon" className="rounded-full" disabled={page >= data.pages} onClick={() => setPage(page + 1)} aria-label="Página siguiente"><ChevronRight className="size-4" /></Button>
            </nav>
          )}
        </section>
      </div>
    </div>
  );
}
