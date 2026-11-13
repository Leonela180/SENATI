import { useState } from "react";
import { ImageUp } from "lucide-react";
import { cn } from "@/lib/utils";

const TYPES = ["image/jpeg", "image/png", "image/webp"];
export const MAX_MB = 10;

/** Solo elige y valida el archivo en el navegador; la subida la hace el estudio al pulsar «Humanizar». */
export function ImageDropzone({ onPick }: { onPick: (file: File) => void }) {
  const [error, setError] = useState("");
  const [over, setOver] = useState(false);

  function pick(f: File | null) {
    setError("");
    if (!f) return;
    if (!TYPES.includes(f.type)) return setError("Solo se aceptan imágenes JPG, PNG o WebP.");
    if (f.size > MAX_MB * 1024 * 1024) return setError(`El archivo supera ${MAX_MB} MB.`);
    onPick(f);
  }

  return (
    <div className="space-y-2">
      <label
        className={cn(
          "group flex min-h-80 cursor-pointer flex-col items-center justify-center gap-4 rounded-3xl border-2 border-dashed bg-card p-8 text-center transition-colors focus-within:ring-2 focus-within:ring-ring",
          over ? "border-brand bg-brand-soft/50" : "hover:border-brand/60 hover:bg-brand-soft/25",
        )}
        onDragOver={(e) => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => { e.preventDefault(); setOver(false); pick(e.dataTransfer.files[0] ?? null); }}
      >
        <span className="grid size-16 place-items-center rounded-2xl bg-brand-soft text-brand-strong transition group-hover:scale-105">
          <ImageUp className="size-7" aria-hidden />
        </span>
        <span className="space-y-1">
          <span className="block font-display text-xl font-semibold">Arrastra tu retrato generado por IA</span>
          <span className="block text-sm text-muted-foreground">o haz clic para elegirlo · JPG, PNG o WebP · hasta {MAX_MB} MB</span>
        </span>
        <input type="file" accept={TYPES.join(",")} className="sr-only" aria-label="Seleccionar imagen"
               onChange={(e) => pick(e.target.files?.[0] ?? null)} />
      </label>
      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
