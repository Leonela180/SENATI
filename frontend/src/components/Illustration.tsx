import { useState } from "react";
import { cn } from "@/lib/utils";

/*
 * Ilustraciones del CONCEPTO para la landing. No son fotos ni resultados del modelo:
 * a la izquierda, piel lisa y brillante («plástica»); a la derecha, la misma piel con microtextura
 * y luz más suave. Se rotulan siempre como ilustración (skill: no mostrar resultados falsos).
 */

const FACE = "M262 34C186 34 132 92 128 166c-2 30-8 46-22 66-8 12-4 20 8 22-2 10 2 16 4 22-4 8 0 16 8 18-2 18 4 32 30 34 18 2 28 14 28 38v134h216V34Z";
const HAIR = "M136 150C134 78 192 26 272 26c78 0 128 58 128 140v230c-26-22-46-52-58-88-10-58-38-98-84-112-34-36-80-50-122-46Z";

/** Retrato editorial abstracto (perfil). textured = microtextura y luz suave; si no, piel lisa con brillo duro. */
function Portrait({ textured }: { textured: boolean }) {
  const id = textured ? "t" : "s";
  return (
    <svg viewBox="0 0 400 500" preserveAspectRatio="xMidYMid slice" className="absolute inset-0 h-full w-full" aria-hidden>
      <defs>
        <radialGradient id={`bg-${id}`} cx="25%" cy="20%" r="90%">
          <stop offset="0" stopColor="oklch(0.62 0.1 52)" /><stop offset=".55" stopColor="oklch(0.36 0.05 42)" /><stop offset="1" stopColor="oklch(0.22 0.03 40)" />
        </radialGradient>
        <linearGradient id={`skin-${id}`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor={textured ? "oklch(0.84 0.06 62)" : "oklch(0.88 0.045 65)"} />
          <stop offset=".6" stopColor={textured ? "oklch(0.7 0.08 50)" : "oklch(0.76 0.06 55)"} />
          <stop offset="1" stopColor="oklch(0.52 0.07 42)" />
        </linearGradient>
        <clipPath id={`face-${id}`}><path d={FACE} /></clipPath>
        <filter id={`grain-${id}`} x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="3" seed="7" />
          <feColorMatrix values="0 0 0 0 .35  0 0 0 0 .2  0 0 0 0 .12  0 0 0 .55 0" />
        </filter>
        <radialGradient id={`gloss-${id}`} cx="50%" cy="50%" r="50%">
          <stop offset="0" stopColor="#fff" stopOpacity={textured ? ".22" : ".85"} /><stop offset="1" stopColor="#fff" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect width="400" height="500" fill={`url(#bg-${id})`} />
      <path d={FACE} fill={`url(#skin-${id})`} />
      <g clipPath={`url(#face-${id})`}>
        {textured && <rect width="400" height="500" filter={`url(#grain-${id})`} opacity=".9" />}
        <ellipse cx={textured ? 200 : 190} cy="200" rx={textured ? 70 : 34} ry={textured ? 55 : 22} fill={`url(#gloss-${id})`} />
        {textured && [[176, 232], [190, 241], [205, 229], [168, 250], [214, 246]].map(([x, y]) => (
          <circle key={`${x}-${y}`} cx={x} cy={y} r="1.6" fill="oklch(0.5 0.07 40)" opacity=".45" />
        ))}
      </g>
      {/* Luz de borde suave (solo en el resultado) */}
      {textured && <path d={FACE} fill="none" stroke="oklch(0.93 0.05 70)" strokeOpacity=".45" strokeWidth="3" />}
      <path d="M150 168c8-4 18-4 26 0" stroke="oklch(0.28 0.03 40)" strokeWidth="3" strokeLinecap="round" fill="none" opacity=".8" />
      {textured && <circle cx="160" cy="171" r="1.8" fill="#fff" opacity=".9" />}
      <path d={HAIR} fill="oklch(0.2 0.025 40)" />
      {textured && <path d="M170 92c40-46 120-60 180-20M200 70c60-30 130-14 172 40M246 50c70 0 118 46 136 120M300 120c34 30 52 80 56 150M270 140c30 26 50 66 58 120" stroke="oklch(0.45 0.045 48)" strokeOpacity=".6" strokeWidth="1.3" fill="none" strokeLinecap="round" />}
    </svg>
  );
}

export function ConceptCompare({ className }: { className?: string }) {
  const [pos, setPos] = useState(52);
  return (
    <figure className={cn("space-y-3", className)}>
      <div className="relative aspect-[4/5] select-none overflow-hidden rounded-[1.75rem] shadow-2xl shadow-[oklch(0.4_0.05_40/0.25)] ring-1 ring-black/5">
        <Portrait textured />
        <div className="absolute inset-0" style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }}><Portrait textured={false} /></div>
        <div aria-hidden className="pointer-events-none absolute inset-y-0 w-px bg-white/90" style={{ left: `${pos}%` }}>
          <span className="absolute top-1/2 left-1/2 grid size-10 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full bg-white text-sm text-foreground shadow-lg">⇆</span>
        </div>
        <span className="absolute top-4 left-4 rounded-full bg-black/55 px-3 py-1 text-xs font-medium text-white backdrop-blur">Antes · piel plástica</span>
        <span className="absolute top-4 right-4 rounded-full bg-white/85 px-3 py-1 text-xs font-medium text-foreground backdrop-blur">Después · textura natural</span>
        <input type="range" min={0} max={100} value={pos} onChange={(e) => setPos(Number(e.target.value))}
               aria-label="Mover la comparación de la ilustración" className="absolute inset-0 h-full w-full cursor-ew-resize opacity-0" />
      </div>
      <figcaption className="text-center text-xs text-muted-foreground">Ilustración del concepto, no es un resultado del modelo.</figcaption>
    </figure>
  );
}

/** Muestra pequeña «antes / después» para cada aspecto que mejora (piel, ojos, cabello, luz). */
export function Swatch({ kind }: { kind: "piel" | "ojos" | "cabello" | "luz" }) {
  const before: Record<string, string> = {
    piel: "linear-gradient(135deg, oklch(0.84 0.06 60), oklch(0.76 0.07 52))",
    ojos: "radial-gradient(circle at 50% 50%, oklch(0.3 0.03 40) 0 22%, oklch(0.55 0.05 60) 23% 40%, oklch(0.96 0.01 80) 41%)",
    cabello: "linear-gradient(180deg, oklch(0.32 0.04 40), oklch(0.26 0.03 40))",
    luz: "linear-gradient(90deg, oklch(0.95 0.02 80), oklch(0.6 0.06 50))",
  };
  const after: Record<string, string> = {
    piel: before.piel,
    ojos: "radial-gradient(circle at 44% 42%, #fff 0 5%, transparent 6%), radial-gradient(circle at 50% 50%, oklch(0.25 0.03 40) 0 20%, oklch(0.5 0.07 55) 21% 39%, oklch(0.93 0.015 75) 40%)",
    cabello: "repeating-linear-gradient(100deg, oklch(0.34 0.04 40) 0 2px, oklch(0.24 0.03 40) 2px 4px, oklch(0.3 0.04 45) 4px 7px)",
    luz: "radial-gradient(90% 120% at 25% 30%, oklch(0.9 0.04 70), oklch(0.68 0.07 50) 60%, oklch(0.5 0.06 45))",
  };
  return (
    <div className="grid grid-cols-2 gap-1.5" aria-hidden>
      <div className="relative h-16 overflow-hidden rounded-l-xl" style={{ background: before[kind] }} />
      <div className={cn("relative h-16 overflow-hidden rounded-r-xl", (kind === "piel" || kind === "luz") && "grain")} style={{ background: after[kind] }} />
    </div>
  );
}
