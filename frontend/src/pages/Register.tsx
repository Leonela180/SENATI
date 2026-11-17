import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthLayout } from "@/app/layouts/AuthLayout";
import { useRegister } from "@/features/auth/useAuth";

export default function Register() {
  const nav = useNavigate();
  const invitation = useLocation().state as { from?: string; email?: string; display_name?: string } | null;
  const from = invitation?.from ?? "/app";
  const reg = useRegister();
  const [f, setF] = useState({ display_name: invitation?.display_name || "", email: invitation?.email || "", password: "" });
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [k]: e.target.value });
  const corta = f.password.length > 0 && f.password.length < 12;

  return (
    <AuthLayout title="Crea tu cuenta" subtitle="Empieza a humanizar tus retratos generados por IA."
                footer={<>¿Ya tienes cuenta? <Link className="font-medium text-foreground underline underline-offset-4" to="/login" state={{ from }}>Inicia sesión</Link></>}>
      <form className="space-y-5" onSubmit={(e) => { e.preventDefault(); reg.mutate(f, { onSuccess: () => nav(from, { replace: true }) }); }}>
        <div className="space-y-2"><Label htmlFor="name">Nombre</Label>
          <Input id="name" required maxLength={120} autoComplete="name" className="h-11" value={f.display_name} onChange={set("display_name")} /></div>
        <div className="space-y-2"><Label htmlFor="email">Correo</Label>
          <Input id="email" type="email" autoComplete="email" required className="h-11" value={f.email} onChange={set("email")} /></div>
        <div className="space-y-2"><Label htmlFor="password">Contraseña (mínimo 12 caracteres)</Label>
          <Input id="password" type="password" autoComplete="new-password" required minLength={12} className="h-11"
                 aria-describedby="pw-help" value={f.password} onChange={set("password")} />
          <p id="pw-help" className={corta ? "text-xs text-amber-800" : "text-xs text-muted-foreground"}>
            {corta ? `Faltan ${12 - f.password.length} caracteres.` : "Usa una frase larga que recuerdes con facilidad."}
          </p></div>
        {reg.error && <p role="alert" className="rounded-xl bg-red-500/10 p-3 text-sm text-red-700 dark:text-red-300">{(reg.error as Error).message}</p>}
        <Button type="submit" className="h-11 w-full rounded-xl" disabled={reg.isPending}>{reg.isPending ? "Creando…" : "Crear cuenta"}</Button>
      </form>
    </AuthLayout>
  );
}
