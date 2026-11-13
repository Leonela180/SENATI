import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthLayout } from "@/app/layouts/AuthLayout";
import { useLogin } from "@/features/auth/useAuth";

export default function Login() {
  const nav = useNavigate();
  const from = (useLocation().state as { from?: string } | null)?.from ?? "/app";
  const login = useLogin();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <AuthLayout title="Bienvenido de nuevo" subtitle="Ingresa para continuar con tus imágenes."
                footer={<>¿No tienes cuenta? <Link className="font-medium text-foreground underline underline-offset-4" to="/registro" state={{ from }}>Regístrate</Link></>}>
      <form className="space-y-5" onSubmit={(e) => { e.preventDefault(); login.mutate({ email, password }, { onSuccess: () => nav(from, { replace: true }) }); }}>
        <div className="space-y-2"><Label htmlFor="email">Correo</Label>
          <Input id="email" type="email" autoComplete="email" required className="h-11" value={email} onChange={(e) => setEmail(e.target.value)} /></div>
        <div className="space-y-2"><Label htmlFor="password">Contraseña</Label>
          <Input id="password" type="password" autoComplete="current-password" required className="h-11" value={password} onChange={(e) => setPassword(e.target.value)} /></div>
        {login.error && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{(login.error as Error).message}</p>}
        <Button type="submit" className="h-11 w-full rounded-xl" disabled={login.isPending}>{login.isPending ? "Entrando…" : "Entrar"}</Button>
      </form>
    </AuthLayout>
  );
}
