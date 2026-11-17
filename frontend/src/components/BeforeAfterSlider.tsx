import { useState } from "react";
import { cn } from "@/lib/utils";

/** Comparador antes/después: se maneja con mouse, toque y teclado (flechas), RNF-04. */
export function BeforeAfterSlider({ before, after, className, beforeLabel = "Original", afterLabel = "Editado con IA" }: { before: string; after: string; className?: string; beforeLabel?: string; afterLabel?: string }) {
  const [pos, setPos] = useState(50);
  return (
    <figure className={cn("mx-auto w-fit max-w-full space-y-2", className)}>
      <div className="relative select-none overflow-hidden rounded-3xl bg-muted shadow-xl shadow-[oklch(0.4_0.05_40/0.18)] ring-1 ring-black/5">
        <img src={after} alt="Resultado editado con IA" className="block max-h-[70vh] w-auto max-w-full" draggable={false} />
        <img src={before} alt="Imagen original" draggable={false}
             className="absolute inset-0 h-full w-full object-cover"
             style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }} />
        <div aria-hidden className="pointer-events-none absolute inset-y-0 w-0.5 bg-white shadow-[0_0_10px_rgba(0,0,0,.45)]" style={{ left: `${pos}%` }}>
          <span className="absolute top-1/2 left-1/2 grid size-10 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full bg-white text-sm shadow-lg">⇆</span>
        </div>
        <span className="absolute top-3 left-3 rounded-full bg-black/60 px-3 py-1 text-xs font-medium text-white backdrop-blur">{beforeLabel}</span>
        <span className="absolute top-3 right-3 rounded-full bg-white/90 px-3 py-1 text-xs font-medium text-neutral-900 backdrop-blur">{afterLabel}</span>
        <input type="range" min={0} max={100} value={pos} aria-label="Comparar antes y después"
               onChange={(e) => setPos(Number(e.target.value))}
               className="absolute inset-0 h-full w-full cursor-ew-resize opacity-0" />
      </div>
      <figcaption className="text-center text-xs text-muted-foreground">Desliza o usa las flechas del teclado para comparar.</figcaption>
    </figure>
  );
}
