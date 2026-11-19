import { Navigate, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { CalendarClock, History, Images, LayoutDashboard, LogOut, Menu, ShieldCheck, Sparkles, User, Users, Wand2, X } from "lucide-react";
import { useState } from "react";
import { Logo } from "@/components/brand/Logo";
import { useLogout, useMe } from "@/features/auth/useAuth";
import { useHealth } from "@/features/jobs/useJobs";
import { cn } from "@/lib/utils";
import { ApiError } from "@/lib/api";
import { QueryError } from "@/components/PageHeader";
import { UserAvatar } from "@/components/UserAvatar";
import { FloatingAssistant } from "@/components/FloatingAssistant";

type NavItem = { to: string; label: string; icon: typeof Sparkles; end?: boolean };
const SECTIONS: { title: string; items: NavItem[] }[] = [
  { title: "", items: [{ to: "/app", label: "Panel", icon: LayoutDashboard, end: true }] },
  { title: "Imágenes", items: [
    { to: "/app/humanizar", label: "Humanizar", icon: Sparkles },
    { to: "/app/realista", label: "Ilustración a realista", icon: Wand2 },
    { to: "/app/calidad", label: "Mejorar resolución", icon: Images },
    { to: "/app/estudio", label: "Estudio de edición", icon: Wand2 },
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
     isActive ? "bg-primary/10 text-brand-strong font-semibold" : "text-muted-foreground hover:bg-sidebar-accent hover:text-foreground");

export default function AppLayout() {
  const { data: me, isLoading, isError, error, isFetching, refetch } = useMe();
  const { data: health, isError: healthError } = useHealth();
  const logout = useLogout();
  const nav = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  if (isLoading) return <p className="p-10 text-muted-foreground" aria-live="polite">Cargando…</p>;
  if (isError && !(error instanceof ApiError && error.status === 401)) {
    return <main className="mx-auto max-w-xl px-4 py-16"><QueryError onRetry={() => { void refetch(); }} retrying={isFetching} /></main>;
  }
  if (!me) return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;

  const sections = SECTIONS.map((s) => (s.title === "Cuenta" && me.role === "admin"
    ? { ...s, items: [...s.items, { to: "/app/admin", label: "Admin", icon: ShieldCheck }] } : s))
    .map((s) => ({ ...s, items: s.items.filter((i) => i.to !== "/app/realista" || health?.realistic_available === true) }));
  const links = sections.flatMap((s) => s.items);
  const currentPage = links.find((item) => item.end ? location.pathname === item.to : location.pathname.startsWith(item.to))?.label
    ?? (location.pathname.startsWith("/app/generar") ? "Generar con IA"
      : location.pathname.startsWith("/app/trabajos") ? "Detalle del trabajo" : "LUMIA AI");
  const salir = () => logout.mutate(undefined, { onSuccess: () => nav("/") });

  return (
    <div className="min-h-screen bg-background font-sans text-foreground lg:grid lg:grid-cols-[16rem_minmax(0,1fr)]">
      <a href="#contenido" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-background focus:p-2">Saltar al contenido</a>

      {/* Barra lateral (escritorio) */}
      <aside className="lumia-sidebar sticky top-0 hidden h-screen flex-col border-r bg-sidebar p-5 text-foreground lg:flex">
        <div className="px-2 pt-2"><Logo to="/app" /><p className="mt-3 text-xs text-muted-foreground">Tu estudio de imágenes con IA</p></div>
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
          <UserAvatar name={me.display_name} />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{me.display_name}</p>
            <p className="truncate text-xs text-muted-foreground">{me.email}</p>
          </div>
          <button onClick={salir} disabled={logout.isPending} className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground" aria-label="Salir" title="Salir">
            <LogOut className="size-4" aria-hidden />
          </button>
        </div>
      </aside>

      <div className="min-w-0">
        <header className="glass sticky top-0 z-30 hidden items-center justify-between gap-4 border-b px-8 py-4 lg:flex">
          <p className="text-sm text-muted-foreground">Mi espacio <span className="mx-3 text-border" aria-hidden>/</span><span className="font-medium text-foreground">{currentPage}</span></p>
          <span className="inline-flex items-center gap-2 rounded-full border bg-background px-3 py-1.5 text-xs text-muted-foreground">
            <span className={cn("size-2 rounded-full", healthError ? "bg-red-600" : health ? "bg-emerald-600" : "bg-amber-500")} aria-hidden />
            {healthError ? "Sin conexión con la API" : health ? "API disponible" : "Comprobando conexión"}
          </span>
        </header>
        {/* Barra superior (celular y tablet) */}
        <header className="glass sticky top-0 z-30 border-b lg:hidden">
          <div className="flex items-center justify-between px-4 py-3">
            <Logo to="/app" />
            <div className="flex items-center gap-1">
              <button onClick={salir} disabled={logout.isPending} className="rounded-xl p-3 text-muted-foreground hover:bg-muted" aria-label="Salir"><LogOut className="size-5" aria-hidden /></button>
              <button onClick={() => setMenuOpen(!menuOpen)} aria-expanded={menuOpen} aria-controls="menu-movil" className="rounded-xl border bg-card p-3" aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"}>
                {menuOpen ? <X className="size-5" aria-hidden /> : <Menu className="size-5" aria-hidden />}
              </button>
            </div>
          </div>
          <nav id="menu-movil" className={cn("grid grid-cols-2 gap-1 px-3 pb-3", !menuOpen && "hidden")} aria-label="Principal">
            {links.map(({ to, label, icon: Icon, end }) => (
              <NavLink key={to} to={to} end={end} onClick={() => setMenuOpen(false)} className={linkClass}><Icon className="size-4" aria-hidden />{label}</NavLink>
            ))}
          </nav>
        </header>

        {health?.engine === "mock" && (
          <div role="status" className="border-b border-amber-500/30 bg-amber-500/10 px-4 py-2 text-center text-xs text-amber-700 dark:text-amber-300 md:text-sm dark:text-amber-300">
            <strong>Humanización en simulación:</strong> sus resultados no son IA real. El Estudio y Gemini funcionan de forma independiente.
          </div>
        )}
        {health?.engine === "local" && health.runtime === "cpp" && (
          <div role="status" className="border-b bg-brand-soft/40 px-4 py-2 text-center text-xs text-brand-strong md:text-sm">
            <strong>IA local en CPU:</strong> procesa una imagen a la vez y puede tardar unos minutos. Puedes seguir el avance en el historial.
          </div>
        )}
        <main id="contenido" className="relative mx-auto max-w-6xl px-4 py-8 md:px-8 md:py-10">
          {logout.error && <p role="alert" className="mb-6 rounded-xl border border-destructive/25 bg-card p-4 text-sm text-destructive">No se pudo cerrar la sesión. Inténtalo de nuevo.</p>}
          <Outlet />
        </main>
        {location.pathname !== "/app/asistente" && <FloatingAssistant />}
      </div>
    </div>
  );
}
