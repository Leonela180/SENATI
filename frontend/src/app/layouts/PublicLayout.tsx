import { Link, Outlet } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/brand/Logo";

const NAV = [
  { href: "/#herramientas", label: "Herramientas" },
  { href: "/#como-funciona", label: "Cómo funciona" },
  { href: "/#privacidad", label: "Privacidad" },
  { href: "/#preguntas", label: "Preguntas" },
];

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-background font-sans text-foreground">
      <a href="#contenido" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-background focus:p-2">Saltar al contenido</a>
      <header className="glass sticky top-0 z-40 border-b">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-4 py-4 md:px-6">
          <Logo />
          <nav className="hidden items-center gap-7 text-sm text-muted-foreground lg:flex" aria-label="Secciones">
            {NAV.map((n) => <a key={n.href} href={n.href} className="transition hover:text-foreground">{n.label}</a>)}
          </nav>
          <div className="flex items-center gap-1 sm:gap-2">
            <Button variant="ghost" asChild className="px-3"><Link to="/login">Ingresar</Link></Button>
            <Button asChild className="rounded-full px-4 sm:px-5"><Link to="/registro">Crear cuenta</Link></Button>
          </div>
        </div>
      </header>
      <main id="contenido"><Outlet /></main>
      <footer className="border-t bg-card/40">
        <div className="mx-auto grid max-w-6xl gap-8 px-4 py-12 md:grid-cols-[2fr_1fr_1fr] md:px-6">
          <div className="space-y-3">
            <Logo />
            <p className="max-w-sm text-sm text-muted-foreground">
              Humaniza, restaura, edita y organiza tus imágenes. Personaliza tu espacio y colabora con tu equipo. Los originales se conservan y los trabajos continúan en el servidor.
            </p>
          </div>
          <div className="space-y-2 text-sm">
            <p className="font-medium">Producto</p>
            {NAV.slice(0, 3).map((n) => <a key={n.href} href={n.href} className="block text-muted-foreground hover:text-foreground">{n.label}</a>)}
          </div>
          <div className="space-y-2 text-sm">
            <p className="font-medium">Cuenta</p>
            <Link to="/login" className="block text-muted-foreground hover:text-foreground">Ingresar</Link>
            <Link to="/registro" className="block text-muted-foreground hover:text-foreground">Crear cuenta</Link>
          </div>
        </div>
        <p className="border-t py-5 text-center text-xs text-muted-foreground">
          LUMIA AI · Proyecto de Innovación SENATI · {new Date().getFullYear()}
        </p>
      </footer>
    </div>
  );
}
