import { useId } from "react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

/** Marca de LUMIA AI: un destello de luz sobre el degradado del acento elegido (Aurora por defecto). */
export function LogoMark({ className }: { className?: string }) {
  // id único: si hay dos logos y uno está oculto (display:none), el degradado compartido no se pintaría
  const g = `lumia-g-${useId().replace(/:/g, "")}`;
  return (
    <svg viewBox="0 0 32 32" aria-hidden className={cn("size-8 shrink-0 drop-shadow-[0_4px_14px_var(--glow)]", className)}>
      <defs>
        <linearGradient id={g} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="var(--g1)" />
          <stop offset=".55" stopColor="var(--g2)" />
          <stop offset="1" stopColor="var(--g3)" />
        </linearGradient>
      </defs>
      <rect x="1" y="1" width="30" height="30" rx="9" fill={`url(#${g})`} />
      <path d="M16 6.5c1 5 2.6 6.6 7.5 7.5-4.9.9-6.5 2.5-7.5 7.5-1-5-2.6-6.6-7.5-7.5 4.9-.9 6.5-2.5 7.5-7.5Z" fill="white" />
      <circle cx="23.5" cy="22.5" r="1.6" fill="white" opacity=".85" />
    </svg>
  );
}

export function Logo({ to = "/", className, light = false }: { to?: string; className?: string; light?: boolean }) {
  return (
    <Link to={to} className={cn("inline-flex shrink-0 items-center gap-2.5 whitespace-nowrap", className)} aria-label="LUMIA AI, inicio">
      <LogoMark />
      <span className={cn("font-display text-xl font-bold tracking-tight", light && "text-white")}>
        LUMIA <span className="text-gradient">AI</span>
      </span>
    </Link>
  );
}
