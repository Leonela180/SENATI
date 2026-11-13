import { useId } from "react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

/** Marca de LUMIA AI: un destello (luz) sobre un círculo cálido. */
export function LogoMark({ className }: { className?: string }) {
  // id único: si hay dos logos y uno está oculto (display:none), el degradado compartido no se pintaría
  const g = `lumia-g-${useId().replace(/:/g, "")}`;
  return (
    <svg viewBox="0 0 32 32" aria-hidden className={cn("size-8 shrink-0", className)}>
      <defs>
        <linearGradient id={g} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="oklch(0.72 0.1 60)" />
          <stop offset="1" stopColor="oklch(0.52 0.11 40)" />
        </linearGradient>
      </defs>
      <circle cx="16" cy="16" r="15" fill={`url(#${g})`} />
      <path d="M16 7c.9 4.6 2.4 6.1 7 7-4.6.9-6.1 2.4-7 7-.9-4.6-2.4-6.1-7-7 4.6-.9 6.1-2.4 7-7Z" fill="oklch(0.99 0.005 80)" />
    </svg>
  );
}

export function Logo({ to = "/", className, light = false }: { to?: string; className?: string; light?: boolean }) {
  return (
    <Link to={to} className={cn("inline-flex shrink-0 items-center gap-2.5 whitespace-nowrap", className)} aria-label="LUMIA AI, inicio">
      <LogoMark />
      <span className={cn("font-display text-xl font-semibold tracking-tight", light && "text-white")}>
        LUMIA <span className={light ? "text-[oklch(0.82_0.08_65)]" : "text-brand-strong"}>AI</span>
      </span>
    </Link>
  );
}
