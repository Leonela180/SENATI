import { Navigate, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { CalendarClock, History, Images, LayoutDashboard, LogOut, ShieldCheck, Sparkles, User, Users, Wand2, WandSparkles } from "lucide-react";
import { Logo } from "@/components/brand/Logo";
import { useLogout, useMe } from "@/features/auth/useAuth";
import { useHealth } from "@/features/jobs/useJobs";
import { cn } from "@/lib/utils";

type NavItem = { to: string; label: string; icon: typeof Sparkles; end?: boolean };
const SECTIONS: { title: string; items: NavItem[] }[] = [
  { title: "", items: [{ to: "/app", label: "Panel", icon: LayoutDashboard, end: true }] },
  { title: "Imágenes", items: [
    { to: "/app/humanizar", label: "Humanizar", icon: Sparkles },
    { to: "/app/estudio", label: "Estudio de edición", icon: Wand2 },
    { to: "/app/generar", label: "Generar con IA", icon: WandSparkles },
    { to: "/app/galeria", label: "Galería", icon: Images },
    { to: "/app/historial", label: "Historial", icon: History },
  ] },
  { title: "Trabajo", items: [
    { to: "/app/horas", label: "Horario y horas", icon: CalendarClock },
    { to: "/app/equipo", label: "Equipo", icon: Users },
  ] },
  { title: "Cuenta", items: [{ to: "/app/perfil", label: "Perfil", icon: User }] },
];

const linkClass = ({ isActive }: { isActive: boolean }) =>
  cn("flex shrink-0 items-center gap-3 rounded-xl px-3 py-2 text-sm transition",
     isActive ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:bg-sidebar-accent hover:text-foreground");

export default function AppLayout() {
  const { data: me, isLoading, isError } = useMe();
  const { data: health } = useHealth();
  const logout = useLogout();
  const nav = useNavigate();
  const location = useLocation();

  if (isLoading) return <p className="p-10 text-muted-foreground" aria-live="polite">Cargando…</p>;
  if (isError || !me) return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;

  const sections = SECTIONS.map((s) => (s.title === "Cuenta" && me.role === "admin"
    ? { ...s, items: [...s.items, { to: "/app/admin", label: "Admin", icon: ShieldCheck }] } : s));
  const links = sections.flatMap((s) => s.items);
  const salir = () => logout.mutate(undefined, { onSettled: () => nav("/") });
  const initial = me.display_name.trim().charAt(0).toUpperCase() || "?";

  return (
    <div className="min-h-screen bg-background font-sans text-foreground lg:grid lg:grid-cols-[16rem_minmax(0,1fr)]">
      <a href="#contenido" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-background focus:p-2">Saltar al contenido</a>

      {/* Barra lateral (escritorio) */}
      <aside className="sticky top-0 hidden h-screen flex-col border-r bg-sidebar p-5 lg:flex">
        <Logo to="/app" />
        <nav className="mt-8 flex flex-1 flex-col gap-5 overflow-y-auto" aria-label="Principal">
          {sections.map((s) => (
            <div key={s.title || "inicio"} className="space-y-1">
              {s.title && <p className="px-3 text-[11px] font-semibold tracking-[0.14em] text-muted-foreground uppercase">{s.title}</p>}
              {s.items.map(({ to, label, icon: Icon, end }) => (
                <NavLink key={to} to={to} end={end} className={linkClass}><Icon className="size-4" aria-hidden />{label}</NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="flex items-center gap-3 rounded-2xl border bg-card p-3">
          <span className="grid size-9 shrink-0 place-items-center rounded-full bg-brand-soft font-semibold text-brand-strong">{initial}</span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{me.display_name}</p>
            <p className="truncate text-xs text-muted-foreground">{me.email}</p>
          </div>
          <button onClick={salir} className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground" aria-label="Salir" title="Salir">
            <LogOut className="size-4" aria-hidden />
          </button>
        </div>
      </aside>

      <div className="min-w-0">
        {/* Barra superior (celular y tablet) */}
        <header className="sticky top-0 z-30 border-b bg-background/90 backdrop-blur lg:hidden">
          <div className="flex items-center justify-between px-4 py-3">
            <Logo to="/app" />
            <button onClick={salir} className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm text-muted-foreground hover:bg-muted" aria-label="Salir">
              <LogOut className="size-4" aria-hidden /> Salir
            </button>
          </div>
          <nav className="flex gap-1 overflow-x-auto px-3 pb-3" aria-label="Principal">
            {links.map(({ to, label, icon: Icon, end }) => (
              <NavLink key={to} to={to} end={end} className={linkClass}><Icon className="size-4" aria-hidden />{label}</NavLink>
            ))}
          </nav>
        </header>

        {health?.engine === "mock" && (
          <div role="status" className="border-b border-amber-300 bg-amber-50 px-4 py-2 text-center text-xs text-amber-900 md:text-sm">
            <strong>Modo simulación:</strong> el motor de IA real no está activo. Los resultados no son humanización real.
          </div>
        )}
        <main id="contenido" className="mx-auto max-w-6xl px-4 py-8 md:px-8 md:py-10"><Outlet /></main>
      </div>
    </div>
  );
}
