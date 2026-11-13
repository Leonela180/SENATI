import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { LogoMark } from "@/components/brand/Logo";

export default function NotFound() {
  return (
    <div className="grid min-h-[60vh] place-items-center px-4 text-center">
      <div className="space-y-4">
        <LogoMark className="mx-auto size-12" />
        <p className="font-display text-6xl font-semibold">404</p>
        <p className="text-muted-foreground">Esta página no existe.</p>
        <Button asChild className="rounded-full"><Link to="/">Ir al inicio</Link></Button>
      </div>
    </div>
  );
}
