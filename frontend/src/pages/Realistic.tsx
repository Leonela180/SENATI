import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { WandSparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ImageDropzone } from "@/components/ImageDropzone";
import { PageHeader } from "@/components/PageHeader";
import { useUploadToGallery } from "@/features/gallery/useGallery";
import { useCreateJob, useHealth } from "@/features/jobs/useJobs";

export default function Realistic() {
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [character, setCharacter] = useState("adult_person");
  const upload = useUploadToGallery();
  const create = useCreateJob();
  const { data: health } = useHealth();
  const nav = useNavigate();
  const ready = !!health?.realistic_available;
  const busy = upload.isPending || create.isPending;
  async function convert() {
    if (!file || !consent || busy) return;
    try {
      const image = await upload.mutateAsync({ file });
      const job = await create.mutateAsync({ image_id: image.id, tool: "realista", preset: "natural", params: { character }, key: crypto.randomUUID() });
      nav(`/app/trabajos/${job.id}`);
    } catch { /* El error visible corresponde a la etapa que fallo. */ }
  }
  return <div className="mx-auto max-w-4xl space-y-8">
    <PageHeader eyebrow="Laboratorio creativo" title="De ilustración a retrato" description="Explora cómo podría verse un personaje adulto de animación como una persona de apariencia fotográfica." />
    <div className="grid gap-6 md:grid-cols-[1fr_20rem]">
      <section className="space-y-4 rounded-3xl border bg-card p-6"><ImageDropzone onPick={f => { setFile(f); upload.reset(); create.reset(); }} />
        {file && <p className="break-all text-sm font-medium">Seleccionada: {file.name}</p>}
        <label className="block space-y-2 text-sm"><span className="font-medium">Representación del personaje</span><select value={character} onChange={e => setCharacter(e.target.value)} className="w-full rounded-xl border bg-background px-3 py-2"><option value="adult_person">Persona adulta · sin especificar</option><option value="adult_man">Hombre adulto</option><option value="adult_woman">Mujer adulta</option></select><span className="text-xs text-muted-foreground">Elige la apariencia que buscas; LUMIA no identifica automáticamente el género ni la identidad.</span></label>
        <label className="flex gap-3 text-sm"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} className="mt-1 size-4 shrink-0" />Tengo permiso para transformar esta imagen y confirmo que representa un personaje adulto.</label>
        <Button disabled={!file || !consent || busy || !ready} onClick={() => { void convert(); }} className="w-full rounded-xl"><WandSparkles className="size-4" aria-hidden />{busy ? "Preparando trabajo…" : "Crear versión realista"}</Button>
        {!ready && <p role="status" className="text-sm text-muted-foreground">En validación: este modo permanece deshabilitado hasta comprobar su calidad y recursos. No se simula la conversión.</p>}
        {(upload.error || create.error) && <p role="alert" className="text-sm text-destructive">{((upload.error || create.error) as Error).message}</p>}
      </section>
      <aside className="space-y-4 rounded-3xl border bg-secondary/40 p-6 text-sm leading-relaxed"><h2 className="font-semibold">Modo experimental</h2><p>Empieza con una cara adulta de frente, bien iluminada y un solo personaje. Usa una imagen de al menos 256 px por lado. Puede cambiar rasgos y accesorios: es una reinterpretación, no una identificación de una persona real.</p><p>Se ejecuta en CPU, una imagen por vez, y puede tardar varios minutos. La salida se calcula a un máximo de 512 px. Consulta el progreso desde Historial mientras sigues usando la aplicación.</p><p>El resultado sigue siendo sintético y se descarga rotulado. No garantiza recuperar detalles ni una identidad exacta.</p></aside>
    </div>
  </div>;
}
