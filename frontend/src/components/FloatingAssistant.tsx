import { useEffect, useRef, useState } from "react";
import { Bot, GripHorizontal, Minus, RotateCcw } from "lucide-react";
import Assistant from "@/pages/Assistant";
import { useLocation } from "react-router-dom";

export function FloatingAssistant() {
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState({ x: 20, y: 20 });
  const drag = useRef<{ x: number; y: number; right: number; bottom: number } | null>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const location = useLocation();
  useEffect(() => { setOpen(false); }, [location.pathname]);
  const clamp = (x: number, y: number) => ({ x: Math.max(8, Math.min(x, innerWidth - 68)), y: Math.max(8, Math.min(y, innerHeight - 68)) });
  useEffect(() => {
    const resize = () => setPosition(p => clamp(p.x, p.y));
    const openChat = () => setOpen(true);
    const escape = (e: KeyboardEvent) => { if (e.key === "Escape") { setOpen(false); trigger.current?.focus(); } };
    window.addEventListener("resize", resize);
    window.addEventListener("lumia-open-chat", openChat);
    window.addEventListener("keydown", escape);
    return () => { window.removeEventListener("resize", resize); window.removeEventListener("keydown", escape); window.removeEventListener("lumia-open-chat", openChat); };
  }, []);
  return <div className="fixed z-50" style={{ right: position.x, bottom: position.y }}>
    <div hidden={!open} id="floating-chat" role="region" aria-label="Chat de ayuda LUMIA" className="fixed w-[min(26rem,calc(100vw-2rem))] max-h-[min(43rem,calc(100dvh-7rem))] overflow-y-auto rounded-3xl border bg-card shadow-2xl" style={{ right: 16, bottom: 88 }}>
      <div className="sticky top-0 z-10 flex items-center justify-between border-b bg-card p-3">
        <span className="flex items-center gap-2 font-semibold"><Bot className="size-5" aria-hidden />Ayuda LUMIA</span>
        <button aria-label="Minimizar chat" className="rounded-lg p-2 hover:bg-muted" onClick={() => { setOpen(false); trigger.current?.focus(); }}><Minus className="size-4" aria-hidden /></button>
      </div>
      <Assistant compact />
    </div>
    <div className="flex items-center gap-1 rounded-full border bg-card p-1 shadow-xl">
      <button ref={trigger} aria-label={open ? "Cerrar asistente" : "Abrir asistente"} aria-expanded={open} aria-controls="floating-chat" onClick={() => setOpen(!open)} className="grid size-12 place-items-center rounded-full bg-primary text-primary-foreground"><Bot className="size-6" aria-hidden /></button>
      <button aria-label="Mover asistente" title="Arrastra o usa las flechas" className="touch-none rounded-full p-2 text-muted-foreground"
        onPointerDown={e => { drag.current = { x: e.clientX, y: e.clientY, right: position.x, bottom: position.y }; e.currentTarget.setPointerCapture(e.pointerId); }}
        onPointerMove={e => { const d = drag.current; if (d) setPosition(clamp(d.right + d.x - e.clientX, d.bottom + d.y - e.clientY)); }}
        onPointerUp={() => { drag.current = null; }} onPointerCancel={() => { drag.current = null; }}
        onKeyDown={e => { const steps: Record<string, [number, number]> = { ArrowLeft: [20, 0], ArrowRight: [-20, 0], ArrowUp: [0, 20], ArrowDown: [0, -20] }; if (steps[e.key]) { e.preventDefault(); const [x, y] = steps[e.key]; setPosition(p => clamp(p.x + x, p.y + y)); } }}>
        <GripHorizontal className="size-4" aria-hidden />
      </button>
      <button aria-label="Restablecer posición del asistente" title="Restablecer posición" onClick={() => setPosition({ x: 20, y: 20 })} className="rounded-full p-2 text-muted-foreground"><RotateCcw className="size-3" aria-hidden /></button>
    </div>
  </div>;
}
